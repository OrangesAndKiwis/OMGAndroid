"""The un-haircut cluster measurement.

For every vendor shared by >=3 scam-profile PACs (excluding candidate committees
and infrastructure), pull its TOTAL client count across all PACs. Classify:
  distinctive  = few total clients  -> a real coordination link
  generic      = many total clients -> industry noise (everyone uses it)
Then count how many scam-profile PACs are linked by a DISTINCTIVE vendor.

No hand-labeling of "scam vendors" — a vendor is a cluster link purely because
it is RARE and shared, which is the actual coordination signal.
"""
import csv
import re
from collections import defaultdict
import concurrent.futures
import vendor_back as vb

DISTINCTIVE_MAX = 12   # <= this many total clients = distinctive (rare)
MIN_SHARED = 3         # vendor must be shared by >=3 scam-profile PACs

CAND = re.compile(r'\bFOR (CONGRESS|SENATE|GOVERNOR|MAYOR|PRESIDENT|AMERICA|CONGRESS|'
                  r'[A-Z]{2}|MONTANA|FLORIDA|MICHIGAN|OHIO|TEXAS|UTAH|NEVADA|'
                  r'CALIFORNIA|VIRGINIA|ARIZONA|GEORGIA|NEW YORK|NORTH|SOUTH)\b'
                  r'|VICTORY (FUND|COMMITTEE)|COMMITTEE TO ELECT|FRIENDS OF|'
                  r'RE.?ELECT|\bFOR US\b|\bFOR NC\b|\bFOR NY\b')
INFRA = ("INTERNAL REVENUE", "SOUTHWEST AIR", "AMERICAN AIR", "DELTA AIR", "USPS",
         "POSTAL", "ACTION NETWORK", "VERIZON", "COMCAST", "FEDEX", "STAPLES",
         "ZOOM", "MAILCHIMP", "MICROSOFT", "UBER", "MARRIOTT", "HILTON",
         "QUICKBOOKS", "INTUIT", "GOOGLE", "AMAZON", "OLSON REMCHO", "PERKINS COIE")


def excl(v):
    return len(v) < 6 or CAND.search(v) or any(i in v for i in INFRA)


# scam-profile PACs -> vendors, from the widened pull
edges = defaultdict(set)
for r in csv.DictReader(open("scam_vendor_edges.csv")):
    edges[r["committee_id"]].add(r["vendor"])
cc = set(edges)

vendor_scampacs = defaultdict(set)
for cid, vs in edges.items():
    for v in vs:
        if not excl(v):
            vendor_scampacs[v].add(cid)
shared = {v: p for v, p in vendor_scampacs.items() if len(p) >= MIN_SHARED}
print(f"{len(cc)} scam-profile PACs; {len(shared)} vendors shared by >= {MIN_SHARED} "
      f"of them. Pulling total footprint of each ...", flush=True)


def footprint(v):
    clients = vb.payers_of(v, 2024, max_pages=4)   # capped: enough to tell few vs many
    return v, len(clients)


tot = {}
done = 0
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
    for v, ntot in ex.map(footprint, shared):
        tot[v] = ntot
        done += 1
        if done % 15 == 0:
            print(f"  {done}/{len(shared)}", flush=True)

distinctive = {v: p for v, p in shared.items() if tot.get(v, 999) <= DISTINCTIVE_MAX}
generic = {v: p for v, p in shared.items() if tot.get(v, 999) > DISTINCTIVE_MAX}
clustered = {c for p in distinctive.values() for c in p}

print(f"\n=== UN-HAIRCUT CLUSTER RESULT (n={len(cc)} scam-profile PACs) ===")
print(f"  vendors shared by >= {MIN_SHARED} scam PACs: {len(shared)}")
print(f"    of those DISTINCTIVE (<= {DISTINCTIVE_MAX} total clients): {len(distinctive)}")
print(f"    GENERIC (industry mail houses, many clients): {len(generic)}")
print(f"  scam-profile PACs linked by a DISTINCTIVE shared vendor: "
      f"{len(clustered)} / {len(cc)} = {len(clustered)/len(cc)*100:.0f}%")
print(f"\nDISTINCTIVE shared vendors (real coordination links):")
for v, p in sorted(distinctive.items(), key=lambda x: -len(x[1])):
    print(f"  {len(p):>2} scam PACs / {tot[v]:>3} total clients   {v[:34]}")
print(f"\nGENERIC (excluded — everyone uses them):")
for v, p in sorted(generic.items(), key=lambda x: -tot[x[0]])[:10]:
    print(f"  {len(p):>2} scam PACs / {tot[v]:>3} total clients   {v[:34]}")

with open("distinctive_clusters.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["vendor", "scam_pac_clients", "total_clients", "type"])
    for v in shared:
        w.writerow([v, len(shared[v]), tot.get(v, ""),
                    "distinctive" if v in distinctive else "generic"])
