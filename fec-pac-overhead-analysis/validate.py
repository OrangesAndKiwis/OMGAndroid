"""Validation spike: does the core flagging logic flag the known case?

Pulls FEC committee totals for one PAC and computes the share of spend that
went to federal candidates. A PAC is *flagged* when that share < 20% (and it
clears the MIN_TOTAL_SPEND noise filter).

Run before building the full pipeline to prove the metric is correct.
  python validate.py                 # uses Animal Protection PAC, DEMO_KEY
  FEC_API_KEY=... python validate.py C00526558
"""
import os
import sys
import json
import urllib.request

API = "https://api.open.fec.gov/v1"
CANDIDATE_SHARE_THRESHOLD = 0.20
MIN_TOTAL_SPEND = 10_000
CYCLES = (2024, 2026)


def get_totals(committee_id, cycle, api_key):
    url = (
        f"{API}/committee/{committee_id}/totals/"
        f"?cycle={cycle}&api_key={api_key}"
    )
    with urllib.request.urlopen(url, timeout=30) as resp:
        return json.load(resp).get("results", [])


def main():
    committee_id = sys.argv[1] if len(sys.argv) > 1 else "C00526558"
    api_key = os.environ.get("FEC_API_KEY", "DEMO_KEY")
    print(f"Committee {committee_id} (key: "
          f"{'DEMO_KEY' if api_key == 'DEMO_KEY' else 'FEC_API_KEY'})\n")

    for cycle in CYCLES:
        results = get_totals(committee_id, cycle, api_key)
        if not results:
            print(f"  {cycle}: no totals reported")
            continue
        t = results[0]
        disbursements = t.get("disbursements") or 0
        to_candidates = t.get("fed_candidate_committee_contributions") or 0
        if not disbursements:
            print(f"  {cycle}: $0 disbursements")
            continue
        share = to_candidates / disbursements
        flagged = share < CANDIDATE_SHARE_THRESHOLD and disbursements >= MIN_TOTAL_SPEND
        print(f"  {cycle}: disbursements=${disbursements:,.0f}  "
              f"to_candidates=${to_candidates:,.0f}  "
              f"candidate_share={share:.1%}  "
              f"-> {'FLAGGED' if flagged else 'not flagged'}")


if __name__ == "__main__":
    main()
