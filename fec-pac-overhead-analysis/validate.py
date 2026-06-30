"""Validation spike: does the core flagging logic flag the known case?

Pulls FEC committee totals for one PAC and computes the share of spend that
went to federal candidates. A PAC is *flagged* when that share < 20% (and it
clears the MIN_TOTAL_SPEND noise filter).

Run before building the full pipeline to prove the metric is correct.
  python validate.py                 # Animal Protection PAC (C00878165), DEMO_KEY
  FEC_API_KEY=... python validate.py C00878165

Prints the committee name/type/cycles up front so an ID mismatch (e.g. the
wrong C00526558 in early notes) is caught immediately.
"""
import os
import sys
import json
import urllib.request
import urllib.parse
import urllib.error

API = "https://api.open.fec.gov/v1"
CANDIDATE_SHARE_THRESHOLD = 0.20
MIN_TOTAL_SPEND = 10_000
DEFAULT_COMMITTEE = "C00878165"  # Animal Protection PAC (Hybrid PAC)


def fec_get(path, api_key, **params):
    params["api_key"] = api_key
    url = f"{API}/{path}?{urllib.parse.urlencode(params)}"
    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            return json.load(resp).get("results", [])
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return []  # no totals for this committee/cycle
        raise


def main():
    committee_id = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_COMMITTEE
    api_key = os.environ.get("FEC_API_KEY", "DEMO_KEY")
    key_label = "DEMO_KEY" if api_key == "DEMO_KEY" else "FEC_API_KEY"

    detail = fec_get(f"committee/{committee_id}/", api_key)
    if not detail:
        print(f"Committee {committee_id}: not found.")
        return
    c = detail[0]
    print(f"{committee_id}  {c.get('name')!r}")
    print(f"  type: {c.get('committee_type_full')}")
    print(f"  cycles: {c.get('cycles')}   (key: {key_label})\n")

    totals = fec_get(f"committee/{committee_id}/totals/", api_key)
    if not totals:
        print("  no totals reported")
        return

    for t in sorted(totals, key=lambda x: x.get("cycle") or 0, reverse=True):
        cycle = t.get("cycle")
        disbursements = t.get("disbursements") or 0
        to_candidates = t.get("fed_candidate_committee_contributions") or 0
        indep_exp = t.get("independent_expenditures") or 0
        if not disbursements:
            print(f"  {cycle}: $0 disbursements -> skipped (below MIN_TOTAL_SPEND)")
            continue
        share = to_candidates / disbursements
        flagged = share < CANDIDATE_SHARE_THRESHOLD and disbursements >= MIN_TOTAL_SPEND
        print(f"  {cycle}: disbursements=${disbursements:,.0f}  "
              f"to_candidates=${to_candidates:,.0f}  "
              f"indep_exp=${indep_exp:,.0f}  "
              f"candidate_share={share:.1%}  "
              f"-> {'FLAGGED' if flagged else 'not flagged'}")


if __name__ == "__main__":
    main()
