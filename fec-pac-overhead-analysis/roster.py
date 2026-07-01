"""Vendor-back rosters for the two newly-confirmed hidden operators.

For each vendor, pull EVERY committee that pays it (2022+2024), with names and
amounts, and flag which clients are already-known scam-profile PACs vs. NEW
committees the earlier screens never surfaced.
"""
import csv
from collections import defaultdict
import vendor_back as vb

VENDORS = ["PUBLIC SUPPORT SERVICES", "DIRECT SUPPORT SERVICES"]
CYCLES = (2022, 2024)

known = {r["committee_id"]: r["name"] for r in csv.DictReader(open("flagged_pacs.csv"))}
scam = {r["committee_id"] for r in csv.DictReader(open("case_candidates.csv"))}

allrows = []
for vendor in VENDORS:
    agg = defaultdict(float)
    for cyc in CYCLES:
        for cid, (amt, _) in vb.payers_of(vendor, cyc, max_pages=12).items():
            agg[cid] += amt
    print(f"\n=== {vendor}: {len(agg)} client committees, "
          f"${sum(agg.values()):,.0f} (2022+2024) ===")
    print(f"{'amount':>12}  {'flag':<10} committee")
    for cid, amt in sorted(agg.items(), key=lambda x: -x[1]):
        nm = known.get(cid) or vb.committee_name(cid)
        flag = "SCAM" if cid in scam else ("known" if cid in known else "NEW")
        print(f"{amt:>12,.0f}  {flag:<10} {cid}  {(nm or '')[:40]}")
        allrows.append({"vendor": vendor, "committee_id": cid,
                        "committee_name": nm, "amount_2022_2024": round(amt, 2),
                        "flag": flag})

with open("operator_rosters.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["vendor", "committee_id", "committee_name",
                                      "amount_2022_2024", "flag"])
    w.writeheader(); w.writerows(allrows)
print("\n-> operator_rosters.csv")
