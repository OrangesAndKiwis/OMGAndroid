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
MAX_SHARED_FRAC = 0.30  # ...but not >30% of PACs (Google/ActBlue-type vendors
                        # are ubiquitous and link everyone -> not distinctive)


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

    # vendor -> PACs that paid it (overhead only)
    vendor_pacs = defaultdict(set)
    vendor_amt = defaultdict(float)
    for cid, vendor, amt in edges:
        vendor_pacs[vendor].add(cid)
        vendor_amt[vendor] += amt

    # distinctive shared vendors: used by >= MIN_SHARED_PACS but not by more than
    # MAX_SHARED_FRAC of all PACs (ubiquitous vendors link everyone -> noise).
    all_pacs = {p for pacs in vendor_pacs.values() for p in pacs}
    ceiling = max(MIN_SHARED_PACS, int(MAX_SHARED_FRAC * len(all_pacs)))
    uf = UnionFind()
    shared_vendors = {v: pacs for v, pacs in vendor_pacs.items()
                      if MIN_SHARED_PACS <= len(pacs) <= ceiling}
    for pacs in shared_vendors.values():
        pacs = sorted(pacs)
        for other in pacs[1:]:
            uf.union(pacs[0], other)

    # gather clusters (only PACs that ended up linked)
    clusters = defaultdict(set)
    for pac in {p for pacs in shared_vendors.values() for p in pacs}:
        clusters[uf.find(pac)].add(pac)

    rows = []
    for members in clusters.values():
        if len(members) < 2:
            continue
        cvendors = sorted(
            (v for v, pacs in shared_vendors.items() if pacs & members),
            key=lambda v: vendor_amt[v], reverse=True)
        total = sum(vendor_amt[v] for v in cvendors)
        rows.append({
            "num_pacs": len(members),
            "num_shared_vendors": len(cvendors),
            "total_shared_overhead": round(total, 2),
            "committee_ids": "; ".join(sorted(members)),
            "shared_vendors": "; ".join(cvendors[:8]),
        })
    rows.sort(key=lambda r: (r["num_pacs"], r["total_shared_overhead"]),
              reverse=True)

    with open(args.out, "w", newline="") as f:
        cols = ["cluster_id", "num_pacs", "num_shared_vendors",
                "total_shared_overhead", "committee_ids", "shared_vendors"]
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for i, r in enumerate(rows, 1):
            w.writerow({"cluster_id": i, **r})

    print(f"Loaded {len(edges)} overhead edges, "
          f"{len(shared_vendors)} vendors shared by >= {MIN_SHARED_PACS} PACs")
    print(f"Found {len(rows)} multi-PAC cluster(s) -> {args.out}\n")
    for i, r in enumerate(rows[:10], 1):
        print(f"  cluster {i}: {r['num_pacs']} PACs, "
              f"{r['num_shared_vendors']} shared vendors, "
              f"${r['total_shared_overhead']:,.0f} overhead")
        print(f"    vendors: {r['shared_vendors'][:80]}")


if __name__ == "__main__":
    main()
