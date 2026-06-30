"""FEC PAC Overhead Analysis — step 2: vendor layer.

For each flagged PAC, pull itemized Schedule B disbursements (2024), normalize
payee names, categorize spend by purpose, and compute the signals that actually
separate scams from legitimate high-overhead committees:

  - cost_to_raise   = fundraising-purpose spend / receipts   (the treadmill)
  - related_party   = a payee whose name/address matches the committee's own
                      treasurer or address (self-dealing)
  - vendor rollup   = which vendors absorb overhead across many PACs

Reads committee IDs from flagged_pacs.csv (step 1 output) by default.

Usage:
    python vendors.py --committees C00878165          # test one PAC
    FEC_API_KEY=... python vendors.py                 # all flagged PACs

Writes top_vendors.csv (and prints per-committee cost-to-raise / related-party).
See CLAUDE.md for rationale.
"""
import argparse
import csv
import os
import re
import time
import json
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict

API = "https://api.open.fec.gov/v1"
PER_PAGE = 100
EMPTY = {"results": [], "pagination": {"pages": 0}}
THROTTLE = 1.05  # seconds between calls; FEC allows ~60/min
_last_call = [0.0]

# disbursement_description keyword -> purpose bucket
PURPOSE_RULES = [
    ("fundraising", ("LIST ACQ", "LIST RENT", "FUNDRAIS", "DIRECT MAIL",
                     "TELEMARKET", "TEXT MESSAG", "EMAIL", "DIGITAL ACQ",
                     "PROSPECT", "DONOR", "MERCHANT", "PROCESSING FEE",
                     "POSTAGE", "PRINTING", "CALL TIME")),
    ("consulting", ("CONSULT", "STRATEG", "RESEARCH", "MEDIA", "ADVERT",
                    "PRODUCTION", "CREATIVE", "DIGITAL")),
    ("admin", ("LEGAL", "ACCOUNT", "COMPLIANCE", "PAYROLL", "SALAR", "RENT",
               "BANK", "ADMIN", "TRAVEL", "FEC")),
    ("mission", ("CONTRIBUTION", "INDEPENDENT EXP", "DONATION TO")),
]


def fec_get(path, api_key, retries=4, **params):
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


SUFFIXES = re.compile(r"\b(INC|LLC|LLP|CORP|CO|LP|LTD|PLLC|PC|COMPANY)\b\.?")


def normalize_vendor(name):
    if not name:
        return ""
    n = name.upper()
    n = re.sub(r"[.,&/]", " ", n)
    n = SUFFIXES.sub("", n)
    return re.sub(r"\s+", " ", n).strip()


def categorize(desc):
    d = (desc or "").upper()
    for bucket, kws in PURPOSE_RULES:
        if any(k in d for k in kws):
            return bucket
    return "other"


def schedule_b(committee_id, api_key, max_pages):
    """Itemized 2024 disbursements via FEC seek pagination (last_index).

    Page-based paging duplicates/skips rows on sorted Schedule B queries, so we
    follow pagination.last_indexes instead — the only reliable method.
    """
    rows, seek, pages = [], {}, 0
    while pages < max_pages:
        d = fec_get("schedules/schedule_b/", api_key,
                    committee_id=committee_id, two_year_transaction_period=2024,
                    per_page=PER_PAGE, sort="-disbursement_amount", **seek)
        res = d.get("results", [])
        rows.extend(res)
        pages += 1
        idx = d.get("pagination", {}).get("last_indexes") or {}
        if len(res) < PER_PAGE or not idx.get("last_index"):
            break
        seek = {"last_index": idx["last_index"],
                "last_disbursement_amount": idx["last_disbursement_amount"]}
    return rows


def committee_meta(committee_id, api_key):
    res = fec_get(f"committee/{committee_id}/", api_key).get("results", [])
    meta = {"treasurer": None, "street": None, "zip": None, "receipts": 0}
    if res:
        c = res[0]
        meta.update(treasurer=c.get("treasurer_name"), street=c.get("street_1"),
                    zip=c.get("zip"))
    # authoritative 2024 receipts (totals endpoint), used as cost-to-raise denom
    tot = fec_get(f"committee/{committee_id}/totals/", api_key,
                  cycle=2024).get("results", [])
    if tot:
        meta["receipts"] = tot[0].get("receipts") or 0
    # 2026 raised-to-date exposure (per-suspect, not a full bulk sweep)
    tot26 = fec_get(f"committee/{committee_id}/totals/", api_key,
                    cycle=2026).get("results", [])
    meta["raised_2026"] = (tot26[0].get("receipts") or 0) if tot26 else 0
    return meta


def related_party(payee, city, zipc, meta):
    """Heuristic self-dealing check.

    Requires the treasurer's surname to appear in the payee name. A bare
    zip-code match is deliberately NOT enough: shared political office
    buildings (e.g. 122 C St NW, 20001) would produce mass false positives.
    Street-level address matching is a future improvement (needs the payee
    street field + entity resolution).
    """
    tre = (meta.get("treasurer") or "").upper()
    surname = tre.split(",")[0].strip() if tre else ""
    return bool(surname and len(surname) > 3 and surname in (payee or "").upper())


def load_committee_ids(args):
    """Committee ids to analyze. From --committees, or the top suspects in the
    flagged file ranked by 2024 receipts (most money at risk first)."""
    if args.committees:
        return args.committees.split(",")
    rows = list(csv.DictReader(open(args.flagged)))

    def receipts(r):
        try:
            return float(r.get("receipts_2024") or 0)
        except ValueError:
            return 0.0

    rows.sort(key=receipts, reverse=True)
    ids = [r["committee_id"] for r in rows]
    return ids[: args.limit] if args.limit else ids


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--committees", help="comma-separated committee ids")
    ap.add_argument("--flagged", default="flagged_pacs.csv")
    ap.add_argument("--limit", type=int, help="max committees")
    ap.add_argument("--max-pages", type=int, default=5,
                    help="Schedule B pages per committee")
    ap.add_argument("--out", default="top_vendors.csv")
    ap.add_argument("--edges", default="pac_vendor_edges.csv",
                    help="PAC<->vendor edge list for clustering (step 3)")
    args = ap.parse_args()

    api_key = os.environ.get("FEC_API_KEY", "DEMO_KEY")
    ids = load_committee_ids(args)
    print(f"Vendor layer over {len(ids)} committee(s) "
          f"(key: {'DEMO_KEY' if api_key == 'DEMO_KEY' else 'FEC_API_KEY'})\n")

    vendors = defaultdict(lambda: {"amount": 0.0, "payments": 0,
                                   "pacs": set(), "purposes": defaultdict(float),
                                   "raw": set(), "places": set()})
    edges = defaultdict(lambda: {"amount": 0.0, "purpose": ""})  # (pac,vendor)
    summaries = []
    for cid in ids:
        meta = committee_meta(cid, api_key)
        rows = schedule_b(cid, api_key, args.max_pages)
        buckets = defaultdict(float)
        total = rel_party_amt = 0.0
        for r in rows:
            amt = r.get("disbursement_amount") or 0
            if amt == 0:
                continue  # keep negatives so refunds net out
            payee = r.get("recipient_name")
            norm = normalize_vendor(payee)
            bucket = categorize(r.get("disbursement_description"))
            buckets[bucket] += amt
            total += amt
            if related_party(payee, r.get("recipient_city"),
                             r.get("recipient_zip"), meta):
                rel_party_amt += amt
            v = vendors[norm]
            v["amount"] += amt
            v["payments"] += 1
            v["pacs"].add(cid)
            v["purposes"][bucket] += amt
            v["raw"].add((payee or "")[:40])
            if r.get("recipient_city"):
                v["places"].add(f"{r.get('recipient_city')},{r.get('recipient_state')}")
            e = edges[(cid, norm)]
            e["amount"] += amt
            e["purpose"] = bucket
        # cost-to-raise uses AUTHORITATIVE receipts (totals endpoint); Schedule B
        # sums are inflated by amended/superseded transactions, so they are used
        # only for vendor identification and relative allocation, not as totals.
        fundraising = buckets.get("fundraising", 0)
        receipts = meta.get("receipts") or 0
        ctr = fundraising / receipts if receipts else 0
        summaries.append({
            "committee_id": cid,
            "treasurer": meta.get("treasurer"),
            "receipts_2024": round(receipts, 2),
            "itemized_net_2024": round(total, 2),
            "fundraising_spend": round(fundraising, 2),
            "cost_to_raise_pct": round(ctr * 100, 1),
            "related_party_spend": round(rel_party_amt, 2),
            "raised_2026_to_date": round(meta.get("raised_2026") or 0, 2),
        })
        print(f"{cid}  itemized=${total:,.0f} (net)  receipts=${receipts:,.0f}  "
              f"cost_to_raise=${fundraising:,.0f}/{ctr:.0%}  "
              f"related_party=${rel_party_amt:,.0f}  "
              f"2026=${meta.get('raised_2026') or 0:,.0f}  "
              f"treasurer={meta.get('treasurer')}")

    # rank vendors by total overhead dollars across PACs
    ranked = sorted(vendors.items(), key=lambda kv: kv[1]["amount"], reverse=True)
    with open(args.out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["vendor_normalized", "total_amount", "num_payments",
                    "num_pacs", "dominant_purpose", "example_name", "places"])
        for norm, v in ranked:
            if not norm:
                continue
            dom = max(v["purposes"].items(), key=lambda kv: kv[1])[0] if v["purposes"] else ""
            w.writerow([norm, round(v["amount"], 2), v["payments"],
                        len(v["pacs"]), dom, sorted(v["raw"])[0],
                        "; ".join(sorted(v["places"])[:3])])
    with open(args.edges, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["committee_id", "vendor_normalized", "amount", "purpose"])
        for (cid, norm), e in edges.items():
            if norm:
                w.writerow([cid, norm, round(e["amount"], 2), e["purpose"]])

    if summaries:
        summaries.sort(key=lambda s: s["cost_to_raise_pct"], reverse=True)
        with open("suspects_summary.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(summaries[0].keys()))
            w.writeheader()
            w.writerows(summaries)

    print(f"\nWrote {args.out}  ({sum(1 for n in vendors if n)} vendors)")
    print(f"Wrote {args.edges}  ({sum(1 for (_, n) in edges if n)} edges)")
    print(f"Wrote suspects_summary.csv  ({len(summaries)} suspects)\n")
    print(f"{'vendor':32} {'total':>12} {'pacs':>5} {'purpose':>12}")
    for norm, v in ranked[:12]:
        if not norm:
            continue
        dom = max(v["purposes"].items(), key=lambda kv: kv[1])[0] if v["purposes"] else ""
        print(f"{norm[:32]:32} {v['amount']:>12,.0f} {len(v['pacs']):>5} {dom:>12}")


if __name__ == "__main__":
    main()
