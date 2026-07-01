"""Widen the vendor analysis from the band to ALL 206 scam-profile PACs, to get
the real vendor-cluster share (vs. the 23%-sample estimate).

For each scam-profile PAC not already analyzed, pull its top Schedule B vendors,
then compute how many of the 206 are (a) linked to a flagged scam-concentrated /
convicted-operator vendor, and (b) share a distinctive vendor with another
scam-profile PAC (a cluster).
"""
import csv
import re
from collections import defaultdict
import concurrent.futures
import vendor_back as vb

SUFFIX = re.compile(r"\b(INC|LLC|LLP|CORP|CO|LP|LTD|PLLC|PC|COMPANY)\b\.?")
STOP = ("WINRED", "ACTBLUE", "ANEDOT", "STRIPE", "PAYPAL", "SQUARE", "GOOGLE",
        "META", "FACEBOOK", "AMAZON", "NGP VAN", "GUSTO", "TATANGO", "USPS",
        "AMERICAN EXPRESS", "BANK", "AUTHORIZE", "PARAGON", "SANDLER REIFF",
        "ELIAS LAW", "NATIONBUILDER", "COMPLIANCE", "CPA", "PAYROLL", "MERCHANT",
        "PAYCHEX", "VERIZON", "AT&T", "COMCAST", "PITNEY BOWES", "COSTCO")


def norm(name):
    if not name:
        return ""
    n = re.sub(r"[.,&/]", " ", name.upper())
    return re.sub(r"\s+", " ", SUFFIX.sub("", n)).strip()


def stop(v):
    return not v or len(v) < 6 or any(s in v for s in STOP)


def sched_b(cid, max_pages=3):
    seek, pages, out = {}, 0, defaultdict(float)
    while pages < max_pages:
        d = vb.get("schedules/schedule_b/", committee_id=cid,
                   two_year_transaction_period=2024, per_page=100,
                   sort="-disbursement_amount", **seek)
        res = d.get("results", [])
        for r in res:
            amt = r.get("disbursement_amount") or 0
            if amt <= 0:
                continue
            v = norm(r.get("recipient_name"))
            if not stop(v):
                out[v] += amt
        pages += 1
        idx = d.get("pagination", {}).get("last_indexes") or {}
        if len(res) < 100 or not idx.get("last_index"):
            break
        seek = {"last_index": idx["last_index"],
                "last_disbursement_amount": idx["last_disbursement_amount"]}
    return out


cc = [r["committee_id"] for r in csv.DictReader(open("case_candidates.csv"))]
names = {r["committee_id"]: r["name"] for r in csv.DictReader(open("flagged_pacs.csv"))}

edges = defaultdict(lambda: defaultdict(float))
for r in csv.DictReader(open("pac_vendor_edges_full.csv")):
    edges[r["committee_id"]][r["vendor_normalized"]] += float(r["amount"] or 0)
todo = [c for c in cc if c not in edges]
print(f"{len(cc)} scam-profile PACs; {len(cc)-len(todo)} already have vendors; "
      f"pulling {len(todo)} more ...", flush=True)

done = 0
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
    for cid, vend in zip(todo, ex.map(sched_b, todo)):
        edges[cid] = vend
        done += 1
        if done % 30 == 0:
            print(f"  pulled {done}/{len(todo)}", flush=True)

# flagged scam-concentrated / convicted-operator vendors
flagv = set()
for r in csv.DictReader(open("hidden_operators.csv")):
    if float(r.get("scam_dollar_share_pct") or 0) >= 50:
        flagv.add(r["vendor"])
flagv |= {"CLOUD DATA SERVICES", "LAV SERVICES", "WIRED4DATA", "STANDARD DATA SERVICES",
          "MARKET PROCESS GROUP", "OUTREACH CALLING", "PUBLIC SUPPORT SERVICES"}


def is_flag(v):
    return any(f in v or v in f for f in flagv)


ccset = set(cc)
vendor_scampacs = defaultdict(set)   # vendor -> scam-profile PACs paying it
for cid in cc:
    for v in edges.get(cid, {}):
        if not stop(v):
            vendor_scampacs[v].add(cid)

# distinctive shared vendors: 2..8 scam PACs (cluster link)
cluster_vendors = {v: p for v, p in vendor_scampacs.items() if 2 <= len(p) <= 8}
clustered = {c for p in cluster_vendors.values() for c in p}
flag_linked = {cid for cid in cc if any(is_flag(v) for v in edges.get(cid, {}))}
either = clustered | flag_linked

with open("scam_vendor_edges.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["committee_id", "vendor", "amount"])
    for cid in cc:
        for v, a in edges.get(cid, {}).items():
            w.writerow([cid, v, round(a, 2)])

print(f"\n=== VENDOR-CLUSTER SHARE across ALL {len(cc)} scam-profile PACs ===")
print(f"  linked to a FLAGGED (scam-concentrated/convicted) vendor: {len(flag_linked)}")
print(f"  in a DISTINCTIVE shared-vendor cluster (2-8 scam PACs): {len(clustered)}")
print(f"  EITHER (flag-vendor OR cluster): {len(either)} / {len(cc)} = {len(either)/len(cc)*100:.0f}%")
print(f"  NEITHER (no dodgy/shared vendor found): {len(cc)-len(either)}")
print(f"\nTop shared vendors now linking scam PACs:")
for v, p in sorted(cluster_vendors.items(), key=lambda x: -len(x[1]))[:15]:
    print(f"  {len(p):>2} PACs  {v[:34]}")
