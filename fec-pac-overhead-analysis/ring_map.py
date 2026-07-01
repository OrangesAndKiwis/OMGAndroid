"""Definitive ring map: every confirmed vendor-linked scam cluster, with each
member PAC's 2024 receipts, 2024 small-dollar take, and 2026 raised-to-date.

Assembles PAC->vendor links from all data on disk (band edges, operator rosters,
known-operator networks), keeps only scam-profile PACs (case_candidates), groups
them into rings by shared vendor family, and pulls current 2024+2026 totals.
"""
import csv
from collections import defaultdict
import vendor_back as vb

cc = {r["committee_id"]: r for r in csv.DictReader(open("case_candidates.csv"))}
names = {r["committee_id"]: r["name"] for r in csv.DictReader(open("flagged_pacs.csv"))}

RINGS = [
    ("Police/Veteran (Zeitlin vendors)", ["CLOUD DATA", "LAV SERVICES", "WIRED4DATA", "STANDARD DATA"]),
    ("Faux-charity (Gelvan/Public Support)", ["PUBLIC SUPPORT SERVICES", "MARKET PROCESS", "OUTREACH CALLING"]),
    ("Health-charity (PACSmart)", ["PACSMART"]),
    ("Outreach mail-shop", ["IMAGE DIRECT", "OMEGA LIST", "WASHINGTON INTELLIGENCE",
                            "EXCEL MAILING", "CAMPAIGN FUNDING DIRECT", "AMH PRINT",
                            "RST MARKETING", "FULFILLMENT SOLUTIONS"]),
    ("Telemarketing (Pro Speaking/DS3)", ["PRO SPEAKING", "DS3 MARKETING", "OFFICE EDGE",
                                          "ADVANCED CREATIVE", "OMEGA"]),
]

pac_vendors = defaultdict(set)
for r in csv.DictReader(open("pac_vendor_edges_full.csv")):
    pac_vendors[r["committee_id"]].add(r["vendor_normalized"])
for r in csv.DictReader(open("operator_rosters.csv")):
    pac_vendors[r["committee_id"]].add(r["vendor"])
op_map = {"Zeitlin (convicted)": "CLOUD DATA", "Gelvan (banned)": "PUBLIC SUPPORT SERVICES"}
for r in csv.DictReader(open("vendor_network_clients.csv")):
    pac_vendors[r["committee_id"]].add(op_map.get(r["operator"], r["operator"]))

ring_pacs, assigned = defaultdict(list), set()
for label, subs in RINGS:
    for cid, vs in pac_vendors.items():
        if cid in assigned or cid not in cc:
            continue
        if any(any(s in v for s in subs) for v in vs):
            ring_pacs[label].append(cid)
            assigned.add(cid)


def totals(cid):
    rows = vb.get(f"committee/{cid}/totals/").get("results", [])
    by = {r.get("cycle"): r for r in rows}

    def pick(cyc, k):
        r = by.get(cyc)
        return (r.get(k) or 0) if r else 0
    return {"r24": pick(2024, "receipts"),
            "sd24": pick(2024, "individual_unitemized_contributions"),
            "r26": pick(2026, "receipts")}


out = []
g24 = gsd = g26 = 0
for label, subs in RINGS:
    cids = ring_pacs.get(label, [])
    if not cids:
        continue
    data = {c: totals(c) for c in cids}
    cids.sort(key=lambda c: -data[c]["r24"])
    s24 = sum(data[c]["r24"] for c in cids)
    ssd = sum(data[c]["sd24"] for c in cids)
    s26 = sum(data[c]["r26"] for c in cids)
    g24 += s24; gsd += ssd; g26 += s26
    print(f"\n=== {label} — {len(cids)} PACs | 2024 ${s24:,.0f} "
          f"(small-$ ${ssd:,.0f}) | 2026-to-date ${s26:,.0f} ===")
    print(f"{'2024 rcpt':>12} {'2024 small$':>12} {'2026 todate':>12}  PAC")
    for c in cids:
        d = data[c]
        print(f"{d['r24']:>12,.0f} {d['sd24']:>12,.0f} {d['r26']:>12,.0f}  "
              f"{(names.get(c) or c)[:38]}")
        out.append({"ring": label, "committee_id": c, "name": names.get(c, ""),
                    "receipts_2024": round(d["r24"], 2),
                    "small_dollar_2024": round(d["sd24"], 2),
                    "raised_2026_to_date": round(d["r26"], 2)})

with open("ring_map.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["ring", "committee_id", "name",
                                      "receipts_2024", "small_dollar_2024", "raised_2026_to_date"])
    w.writeheader(); w.writerows(out)
print(f"\n===== TOTAL: {len(out)} vendor-linked scam PACs | "
      f"2024 ${g24:,.0f} (small-$ ${gsd:,.0f}) | 2026-to-date ${g26:,.0f} =====")
print("-> ring_map.csv")
