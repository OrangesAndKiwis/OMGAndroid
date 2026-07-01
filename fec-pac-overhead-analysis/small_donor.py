"""Receipts-side screen: PACs that harvest small-dollar donors but give ~0 to
candidates — the "preys on ordinary/vulnerable people" fingerprint most relevant
to a consumer-deception case.

Adds the dimension the disbursement screen (analyze.py) misses: WHERE the money
comes from. A committee raising most of its money in **unitemized** individual
contributions (<$200, i.e. small donors) while passing almost nothing to
candidates is the classic scam-PAC-of-small-donors profile.

    python small_donor.py

Writes case_candidates.csv, ranked by small-dollar dollars at risk.
"""
import csv
import os

import analyze  # reuse concurrent bulk sweep + fec_get

SMALL_DOLLAR_MIN = 0.50    # >=50% of receipts from unitemized (<$200) donors
MISSION_MAX = 0.20         # <20% of spend to candidates + IEs
RECEIPTS_FLOOR = 100_000   # meaningful money at stake
PARTY = {"X", "Y", "Z"}
EXCLUDE_DESIG = {"J"}      # JFCs


def load_watchlist_hits(path="scored_leads.csv"):
    hits = {}
    try:
        for r in csv.DictReader(open(path)):
            w = float(r.get("watchlist_vendor_spend") or 0)
            if w > 0:
                hits[r["committee_id"]] = w
    except FileNotFoundError:
        pass
    return hits


def main():
    api_key = os.environ.get("FEC_API_KEY", "DEMO_KEY")
    print("Sweeping 2024 PAC totals for small-dollar profile ...")
    rows = analyze.sweep_totals(2024, api_key, min_disbursements=10000)
    print(f"  scanned {len(rows)} committees")
    watch = load_watchlist_hits()

    out = []
    for r in rows:
        if r.get("committee_type") in PARTY:
            continue
        if r.get("committee_designation") in EXCLUDE_DESIG:
            continue
        receipts = r.get("receipts") or 0
        disb = r.get("disbursements") or 0
        if receipts < RECEIPTS_FLOOR or disb <= 0:
            continue
        unitemized = r.get("individual_unitemized_contributions") or 0
        small_share = unitemized / receipts
        mission = ((r.get("fed_candidate_committee_contributions") or 0)
                   + (r.get("independent_expenditures") or 0)) / disb
        if small_share < SMALL_DOLLAR_MIN or mission >= MISSION_MAX:
            continue
        oper = r.get("operating_expenditures") or 0
        cid = r.get("committee_id")
        out.append({
            "committee_id": cid,
            "name": r.get("committee_name"),
            "designation": r.get("committee_designation"),
            "receipts_2024": round(receipts, 2),
            "small_dollar_raised": round(unitemized, 2),
            "small_dollar_pct": round(small_share * 100, 1),
            "to_candidates_ie_pct": round(mission * 100, 1),
            "overhead_pct": round(oper / disb * 100, 1),
            "watchlist_vendor_spend": round(watch.get(cid, 0), 2),
        })

    # rank by small-dollar dollars harvested (aggregate class exposure)
    out.sort(key=lambda x: x["small_dollar_raised"], reverse=True)
    with open("case_candidates.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys()))
        w.writeheader()
        w.writerows(out)

    total = sum(x["small_dollar_raised"] for x in out)
    print(f"\n{len(out)} case-candidate PACs "
          f"(>= {SMALL_DOLLAR_MIN:.0%} small-dollar, < {MISSION_MAX:.0%} to candidates, "
          f">= ${RECEIPTS_FLOOR:,})")
    print(f"aggregate small-dollar money harvested (2024): ${total:,.0f}")
    print(f"-> case_candidates.csv\n")
    print(f"{'small$raised':>12} {'small%':>7} {'toCand%':>8} {'oh%':>5} "
          f"{'watchlist':>10}  name")
    for x in out[:25]:
        flag = "  <-- convicted-operator vendor" if x["watchlist_vendor_spend"] else ""
        print(f"{x['small_dollar_raised']:>12,.0f} {x['small_dollar_pct']:>6.0f}% "
              f"{x['to_candidates_ie_pct']:>7.1f}% {x['overhead_pct']:>4.0f}% "
              f"{x['watchlist_vendor_spend']:>10,.0f}  {(x['name'] or '')[:30]}{flag}")


if __name__ == "__main__":
    main()
