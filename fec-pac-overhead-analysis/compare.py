"""Threshold-exploration spike: show all three candidate ratios side-by-side.

For a labeled sample of committees (a documented scam PAC, legitimate Super
PACs / party committees, and our validation case), pull the most recent cycle
with real spend and print:

  overhead   = operating_expenditures / disbursements         (Option C metric)
  contrib    = fed_candidate_committee_contributions / disb   (Option A, status quo)
  mission    = (contributions_to_candidates + indep_exp) / disb (Option B)

Goal: eyeball where to set the overhead threshold so legit Super PACs DON'T
trip it and scam-style PACs DO.

  python compare.py            # default labeled sample, DEMO_KEY
  FEC_API_KEY=... python compare.py
"""
import os
import json
import urllib.request
import urllib.parse
import urllib.error

API = "https://api.open.fec.gov/v1"

# (committee_id, label) — a deliberate spread of structures.
SAMPLE = [
    ("C00878165", "Animal Protection PAC (validation, Hybrid)"),
    ("C00479980", "Put Vets First (documented scam PAC)"),
    ("C00571703", "Senate Leadership Fund (legit Super PAC)"),
    ("C00000935", "DCCC (legit party/connected)"),
]


def fec_get(path, api_key, **params):
    params["api_key"] = api_key
    url = f"{API}/{path}?{urllib.parse.urlencode(params)}"
    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            return json.load(resp).get("results", [])
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return []
        raise


TARGET_CYCLE = 2024  # last COMPLETED cycle; 2026 is mid-cycle and misleading


def latest_total(committee_id, api_key):
    """Totals for TARGET_CYCLE, else most recent cycle with non-zero spend."""
    rows = [r for r in fec_get(f"committee/{committee_id}/totals/", api_key)
            if (r.get("disbursements") or 0) > 0]
    if not rows:
        return None
    for r in rows:
        if r.get("cycle") == TARGET_CYCLE:
            return r
    return max(rows, key=lambda r: r.get("cycle") or 0)


def main():
    api_key = os.environ.get("FEC_API_KEY", "DEMO_KEY")
    print(f"{'committee / label':<46} {'cycle':>5} {'receipts':>14} "
          f"{'overhead':>9} {'contrib':>8} {'mission':>8}")
    print("-" * 96)
    rows = []
    for cid, label in SAMPLE:
        t = latest_total(cid, api_key)
        if not t:
            print(f"{label:<46} {'—':>5}  (no totals with spend)")
            continue
        d = t["disbursements"]
        oper = t.get("operating_expenditures") or 0
        contrib = t.get("fed_candidate_committee_contributions") or 0
        ie = t.get("independent_expenditures") or 0
        receipts = t.get("receipts") or 0
        overhead = oper / d
        contrib_r = contrib / d
        mission = (contrib + ie) / d
        rows.append((overhead, label, t.get("cycle"), receipts,
                     overhead, contrib_r, mission))
    # sort most-overhead first — that's the scam-suspicion ordering
    for _, label, cycle, receipts, overhead, contrib_r, mission in sorted(
            rows, reverse=True):
        print(f"{label:<46} {cycle:>5} {receipts:>14,.0f} "
              f"{overhead:>8.1%} {contrib_r:>7.1%} {mission:>7.1%}")
    print("\noverhead = operating_exp / disbursements   (high = suspicious)")
    print("contrib  = candidate contributions / disbursements   (status quo)")
    print("mission  = (contributions + indep_exp) / disbursements")


if __name__ == "__main__":
    main()
