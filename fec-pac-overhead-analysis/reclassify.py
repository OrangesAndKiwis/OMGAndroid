"""Offline reclassification of the distinctive shared-vendor result — no API.

The raw run found 76 recipients that are RARE (<=12 total clients) and shared by
>=3 scam-profile PACs -> 54% of PACs linked. But "rare + shared" also catches
recipients that are not commercial vendors and are rare for structural reasons:
  PROCESSOR  ActBlue/WinRed technical services, banks  (conduits, not vendors)
  COMMITTEE  candidate cmtes / other PACs / JFCs        (transfers, not vendors)
  PERSON     individual treasurers paid directly        (one person, few cmtes)
A genuine coordination link is a commercial FUNDRAISING/TELEFUND/MAIL/DATA vendor
shared by several PACs. This splits the 76 into those buckets — every recipient
shown, nothing hand-labeled as "scam" — and reports the de-contaminated share.
"""
import csv
import re
from collections import defaultdict

DISTINCTIVE_MAX = 12
MIN_SHARED = 3

# reuse the SAME candidate/infra exclusions as the main run
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


# --- bucket classifiers (transparent, pattern-based, no per-vendor hand-labels) ---
PROCESSOR = ("ACTBLUE", "WINRED", "ANEDOT", "STRIPE", "PAYPAL", "SQUARE",
             "AMALGAMATED BANK", "TECHNICAL SERVICES", "VALIDITY", "SWITCHBOARD PBC")
# recipient is itself a political committee (transfer/earmark, not a vendor)
CMTE = re.compile(
    r'\bPAC\b|POLITICAL ACTION|\bFOR (ATTORNEY|CITY|COUNTY|STATE|MAYOR|COUNCIL|'
    r'CONTROLLER|TREASURER|SHERIFF|JUDGE|SENATE|CONGRESS|ASSEMBLY|SUPERVISOR|'
    r'GOVERNOR|PRESIDENT|PHILLY|THE )|JOINT FUNDR|VICTORY|SAVE AMERICA|'
    r'\b47 COMMITTEE\b|TURNOUT PROJECT|COLLECTIVE ACTION|MAJORITY|ASSOCIATION OF '
    r'SECRETAR|CONFERENCE OF THE|CAMPAIGN COMMITTEE|DEMOCRATIC ASSOCIATION|'
    r'\bCOMMITTEE\b|CULAC|EDUCATION (COMMITTEE|FUND)|\bFAMILIES\b|MIDDLE OF THE ROAD|'
    r'\bDEELEY 15\b|ROSS COMMITTEE|PASCAL')
# looks like a single individual (treasurer paid directly): two tokens, both words,
# no corporate/industry token
INDUSTRY = ("DATA", "MAIL", "MEDIA", "MARKETING", "PRINT", "FULFILL", "STRATEG",
            "CONSULT", "DIGITAL", "DIRECT", "CAGING", "LIST", "GROUP", "SERVICES",
            "SOLUTIONS", "PARTNERS", "CREATIVE", "RESPONSE", "LOGISTICS", "PRODUCTION",
            "MULTIMEDIA", "MULTI-MEDIA", "RESOURCES", "CONNECTS", "SPEAKING", "EDGE",
            "TECHNOLOG", "INTERACTIVE", "GLOBAL", "CENTER", "CORPORATION", "COM",
            "USA", "RMG", "DS3", "PBC", "STRATEGIES", "GROUP CONSULTANTS",
            "POLITICAL", "MARKET", "PROGRAMS", "RESIDENTIAL", "MOBILIZATION")


def looks_person(v):
    toks = v.split()
    if not (2 <= len(toks) <= 3):
        return False
    if any(any(k in t for k in INDUSTRY) for t in toks):
        return False
    # all-alpha tokens, no digits, none is a known industry word -> a person's name
    return all(re.fullmatch(r"[A-Z][A-Z'\-]+", t) for t in toks)


def bucket(v):
    if any(p in v for p in PROCESSOR):
        return "PROCESSOR"
    if CMTE.search(v):
        return "COMMITTEE"
    if looks_person(v):
        return "PERSON"
    return "VENDOR"


# --- load cached footprint counts + scam edges (all on disk, no API) ---
# cache is headerless rows of [vendor, total_clients] appended during the run
tot = {row[0]: int(row[1]) for row in csv.reader(open("footprint_cache.csv")) if len(row) == 2}

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
distinctive = {v: p for v, p in shared.items() if tot.get(v, 999) <= DISTINCTIVE_MAX}

by_bucket = defaultdict(dict)
for v, p in distinctive.items():
    by_bucket[bucket(v)][v] = p

# PACs linked by a genuine commercial VENDOR only
real = by_bucket["VENDOR"]
clustered_all = {c for p in distinctive.values() for c in p}
clustered_real = {c for p in real.values() for c in p}

print(f"=== DISTINCTIVE SHARED RECIPIENTS, BUCKETED (n={len(cc)} scam-profile PACs) ===")
print(f"  76 distinctive recipients split by WHAT THE RECIPIENT IS:\n")
for b in ("VENDOR", "COMMITTEE", "PROCESSOR", "PERSON"):
    d = by_bucket[b]
    pacs = {c for p in d.values() for c in p}
    print(f"  {b:<10} {len(d):>2} recipients  -> {len(pacs):>3} scam PACs linked")
print()
print(f"  RAW  (any distinctive recipient):     {len(clustered_all)}/{len(cc)} = {len(clustered_all)/len(cc)*100:.0f}%")
print(f"  CLEAN (genuine commercial VENDOR only): {len(clustered_real)}/{len(cc)} = {len(clustered_real)/len(cc)*100:.0f}%")

print(f"\n--- GENUINE VENDORS (the real coordination links) ---")
for v, p in sorted(real.items(), key=lambda x: -len(x[1])):
    print(f"  {len(p):>2} scam PACs / {tot.get(v,'?'):>3} clients   {v[:38]}")

print(f"\n--- EXCLUDED as COMMITTEE (transfers, not vendors) ---")
for v in sorted(by_bucket['COMMITTEE'], key=lambda x: -len(by_bucket['COMMITTEE'][x])):
    print(f"  {len(by_bucket['COMMITTEE'][v]):>2}  {v[:44]}")
print(f"\n--- EXCLUDED as PROCESSOR/BANK ---")
for v in by_bucket['PROCESSOR']:
    print(f"      {v[:44]}")
print(f"\n--- EXCLUDED as PERSON (individual treasurer) ---")
for v in by_bucket['PERSON']:
    print(f"      {v[:44]}")

with open("distinctive_clusters.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["vendor", "scam_pac_clients", "total_clients", "bucket"])
    for v, p in sorted(shared.items(), key=lambda x: -len(x[1])):
        b = bucket(v) if v in distinctive else "generic"
        w.writerow([v, len(p), tot.get(v, ""), b])
print("\n-> distinctive_clusters.csv")
