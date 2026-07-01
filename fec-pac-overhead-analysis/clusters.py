"""FEC PAC Overhead Analysis — step 3: cluster PACs by shared overhead vendors.

Reads the PAC<->vendor edge list (step 2) and groups flagged PACs that share
overhead vendors (fundraising / consulting / admin). Shared *candidate*
recipients are ignored — two PACs giving to the same candidate is not
suspicious; two PACs routing money through the same fundraising firm is the
signature of a coordinated operation.

Clusters = connected components (union-find) over PACs linked by a shared
overhead vendor used by >= MIN_SHARED_PACS committees. Ranked by operation
size: (# PACs) then total shared overhead dollars.

Usage:
    python clusters.py                       # reads pac_vendor_edges.csv
    python clusters.py --edges other.csv

Writes vendor_clusters.csv.
"""
import argparse
import csv
from collections import defaultdict

OVERHEAD_PURPOSES = {"fundraising", "consulting", "admin"}
MIN_SHARED_PACS = 2     # a vendor must touch >=2 PACs to be a linking edge
MAX_SHARED_FRAC = 0.30  # ...but not >30% of PACs...
MAX_SHARED_PACS = 8     # ...and never more than this absolute count. At scale a
                        # fractional cap is too loose (a vendor in 100 of 752
                        # PACs still blobs them); a distinctive shared vendor
                        # links only a handful of committees.

# Payment processors / platforms / infrastructure everyone uses — they are not
# distinctive fundraising operations, so they must not link PACs into clusters.
STOPLIST = (
    "WINRED", "ACTBLUE", "ANEDOT", "STRIPE", "PAYPAL", "SQUARE",
    "GOOGLE", "META", "FACEBOOK", "AMAZON", "MICROSOFT", "TWILIO",
    "NGP VAN", "SALSA", "USPS", "POSTAL", "AMERICAN EXPRESS", "WELLS FARGO",
    "COMCAST", "VERIZON", "AT&T", "INTUIT", "QUICKBOOKS", "DELTA", "UNITED AIR",
    "AUTHORIZE NET", "PARAGON PAYMENT", "BANK OF AMERICA", "AMALGAMATED BANK",
    "CHASE BANK", "JPMORGAN", "CITIBANK", "HILTON", "MARRIOTT", "EXPEDIA",
    "SOUTHWEST AIR", "AMERICAN AIR", "UBER", "LYFT", "FEDEX", "UPS ",
    # payroll / compliance / law / SaaS — shared services, not fundraising ops
    "GUSTO", "TATANGO", "SANDLER REIFF", "ELIAS LAW", "CAPITOL COMPLIANCE",
    "GRASSROOTS ANALYTICS", "NATIONBUILDER", "DIVVY", "RAMP", "QGIV", "NUMERO",
)


def is_stoplisted(vendor):
    return any(s in vendor for s in STOPLIST)


class UnionFind:
    def __init__(self):
        self.parent = {}

    def find(self, x):
        self.parent.setdefault(x, x)
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[ra] = rb


def load_edges(path):
    edges = []
    with open(path) as f:
        for row in csv.DictReader(f):
            if row["purpose"] in OVERHEAD_PURPOSES:
                edges.append((row["committee_id"], row["vendor_normalized"],
                              float(row["amount"])))
    return edges


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--edges", default="pac_vendor_edges.csv")
    ap.add_argument("--out", default="vendor_clusters.csv")
    args = ap.parse_args()

    edges = load_edges(args.edges)

    # vendor -> PACs that paid it (overhead only, excluding infra/processors)
    vendor_pacs = defaultdict(set)
    vendor_amt = defaultdict(float)
    for cid, vendor, amt in edges:
        if is_stoplisted(vendor):
            continue
        vendor_pacs[vendor].add(cid)
        vendor_amt[vendor] += amt

    # Vendor-centric groups, NOT connected components. At scale, transitive
    # component-chaining collapses everything into one blob (vendor A links
    # {1,2,3}, B links {3,4,5} ... -> one giant component). A distinctive shared
    # vendor and the handful of PACs paying it is the interpretable, actionable
    # unit: "these N flagged PACs all route overhead to the same vendor."
    groups = [{
        "vendor": v,
        "num_pacs": len(pacs),
        "total_overhead": round(vendor_amt[v], 2),
        "committee_ids": "; ".join(sorted(pacs)),
    } for v, pacs in vendor_pacs.items()
        if MIN_SHARED_PACS <= len(pacs) <= MAX_SHARED_PACS]
    groups.sort(key=lambda g: (g["num_pacs"], g["total_overhead"]), reverse=True)

    with open(args.out, "w", newline="") as f:
        cols = ["group_id", "vendor", "num_pacs", "total_overhead", "committee_ids"]
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for i, g in enumerate(groups, 1):
            w.writerow({"group_id": i, **g})

    linked = {p for g in groups for p in g["committee_ids"].split("; ")}
    print(f"Loaded {len(edges)} overhead edges; "
          f"{len(groups)} distinctive shared-vendor groups "
          f"({MIN_SHARED_PACS}-{MAX_SHARED_PACS} PACs each) linking {len(linked)} PACs")
    print(f"-> {args.out}\n")
    for i, g in enumerate(groups[:12], 1):
        print(f"  group {i}: {g['vendor'][:34]:34} {g['num_pacs']} PACs  "
              f"${g['total_overhead']:>12,.0f}")


if __name__ == "__main__":
    main()
