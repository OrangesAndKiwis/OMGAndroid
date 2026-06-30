"""FEC PAC Overhead Analysis — step 1: flag deceptive-overhead PACs.

Sweeps the PAC universe for the completed 2024 cycle via the bulk
/totals/pac/ endpoint, computes the mission ratio
    (fed_candidate_committee_contributions + independent_expenditures)
    / disbursements
and flags committees below MISSION_THRESHOLD that clear MIN_TOTAL_SPEND.
2026 is reported as a raised-to-date exposure column only (never used to flag).

Party committees are excluded (they spend via coordinated expenditures /
transfers and are a false-positive class).

Usage:
    python analyze.py --limit 50          # test run (small, DEMO_KEY-safe)
    FEC_API_KEY=... python analyze.py     # full run

Writes flagged_pacs.csv.  See CLAUDE.md for the methodology rationale.
"""
import argparse
import csv
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request

API = "https://api.open.fec.gov/v1"
MISSION_THRESHOLD = 0.20
MIN_TOTAL_SPEND = 10_000
FLAG_CYCLE = 2024
EXPOSURE_CYCLE = 2026
PARTY_TYPES = {"X", "Y", "Z"}  # party committees — excluded
PER_PAGE = 100


EMPTY = {"results": [], "pagination": {"pages": 0}}
THROTTLE = 1.05  # seconds between calls; FEC allows ~60/min
_last_call = [0.0]


def fec_get(path, api_key, retries=4, **params):
    """GET with pacing + retry/backoff. 404 -> empty; rate-limit/transient -> retry."""
    gap = THROTTLE - (time.time() - _last_call[0])
    if gap > 0:
        time.sleep(gap)
    _last_call[0] = time.time()
    params["api_key"] = api_key
    url = f"{API}/{path}?{urllib.parse.urlencode(params)}"
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(url, timeout=60) as resp:
                return json.load(resp)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return EMPTY
            if e.code in (429, 500, 502, 503) and attempt < retries - 1:
                time.sleep(2 ** attempt)
                continue
            raise
        except (urllib.error.URLError, TimeoutError, ConnectionError):
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
                continue
            raise
    return EMPTY


def sweep_totals(cycle, api_key, limit=None, **filters):
    """Page through bulk /totals/pac/ for a cycle, up to `limit` records.

    Extra `filters` (e.g. min_disbursements) are applied server-side to shrink
    the sweep before paging."""
    rows, page = [], 1
    while True:
        d = fec_get("totals/pac/", api_key, cycle=cycle, per_page=PER_PAGE,
                    page=page, sort="committee_id", **filters)
        results = d.get("results", [])
        if not results:
            break
        rows.extend(results)
        if limit and len(rows) >= limit:
            return rows[:limit]
        if page >= d.get("pagination", {}).get("pages", 0):
            break
        page += 1
    return rows


def receipts_map(cycle, api_key, limit=None):
    """Bulk {committee_id: receipts} for a cycle (single sweep, not per-PAC)."""
    return {r.get("committee_id"): (r.get("receipts") or 0)
            for r in sweep_totals(cycle, api_key, limit=limit)}


def analyze(rows, exposure):
    flagged = []
    skipped_party = skipped_small = 0
    for r in rows:
        ctype = r.get("committee_type")
        if ctype in PARTY_TYPES:
            skipped_party += 1
            continue
        disb = r.get("disbursements") or 0
        if disb < MIN_TOTAL_SPEND:
            skipped_small += 1
            continue
        contrib = r.get("fed_candidate_committee_contributions") or 0
        ie = r.get("independent_expenditures") or 0
        oper = r.get("operating_expenditures") or 0
        receipts = r.get("receipts") or 0
        mission = (contrib + ie) / disb
        if mission >= MISSION_THRESHOLD:
            continue
        raised_2026 = exposure.get(r.get("committee_id"))
        flagged.append({
            "committee_id": r.get("committee_id"),
            "name": r.get("committee_name"),
            "committee_type": r.get("committee_type_full") or ctype,
            "receipts_2024": round(receipts, 2),
            "disbursements_2024": round(disb, 2),
            "overhead_pct": round(oper / disb * 100, 1),
            "mission_pct": round(mission * 100, 1),
            "candidate_pct": round(contrib / disb * 100, 1),
            "indep_exp_2024": round(ie, 2),
            "raised_2026_to_date": "" if raised_2026 is None else round(raised_2026, 2),
            "flag_reason": f"mission {mission:.1%} < {MISSION_THRESHOLD:.0%}",
        })
    flagged.sort(key=lambda x: x["mission_pct"])  # worst first
    return flagged, skipped_party, skipped_small


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=None,
                    help="cap committees scanned (test runs)")
    ap.add_argument("--out", default="flagged_pacs.csv")
    args = ap.parse_args()

    api_key = os.environ.get("FEC_API_KEY", "DEMO_KEY")
    key_label = "DEMO_KEY" if api_key == "DEMO_KEY" else "FEC_API_KEY"
    print(f"Sweeping {FLAG_CYCLE} PAC totals (key: {key_label}, "
          f"limit: {args.limit or 'none'}) ...")

    # min_disbursements applies the MIN_TOTAL_SPEND noise floor server-side,
    # shrinking the sweep (~9200 -> ~6000 committees).
    rows = sweep_totals(FLAG_CYCLE, api_key, limit=args.limit,
                        min_disbursements=MIN_TOTAL_SPEND)
    print(f"  scanned {len(rows)} committees")
    print(f"Fetching {EXPOSURE_CYCLE} raised-to-date (bulk) ...")
    exposure = receipts_map(EXPOSURE_CYCLE, api_key, limit=args.limit)
    flagged, sp, ss = analyze(rows, exposure)
    print(f"  excluded: {sp} party, {ss} below ${MIN_TOTAL_SPEND:,} spend")
    print(f"  FLAGGED: {len(flagged)}")

    if not flagged:
        print("No committees flagged in this slice.")
        return
    cols = list(flagged[0].keys())
    with open(args.out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(flagged)
    print(f"\nWrote {args.out}\n")
    print(f"{'committee_id':12} {'mission%':>8} {'overhead%':>9} "
          f"{'2024 disb':>13} {'2026 to date':>13}  name")
    for r in flagged[:15]:
        exp = r["raised_2026_to_date"]
        exp_s = f"{exp:,.0f}" if isinstance(exp, (int, float)) else "n/a"
        print(f"{r['committee_id']:12} {r['mission_pct']:>7}% {r['overhead_pct']:>8}% "
              f"{r['disbursements_2024']:>13,.0f} {exp_s:>13}  "
              f"{(r['name'] or '')[:32]}")
    if len(flagged) > 15:
        print(f"... and {len(flagged) - 15} more in {args.out}")


if __name__ == "__main__":
    main()
