"""Vendor-BACK view: start from a known scam-fundraiser and find EVERY committee
that pays it — the common-enterprise map the legal case needs.

The rest of the pipeline is PAC-back (PAC -> its vendors). This inverts it:
vendor -> all client PACs + total money moved. This is how the Daily Beast
mapped the $140M Zeitlin network, and it identifies the vendor (the defendant),
its full client roster (the operation), and the aggregate take (the class harm).

    python vendor_back.py

Writes vendor_networks.csv (per operator) and vendor_network_clients.csv (edges).
"""
import csv
import os
import threading
import time
import json
import urllib.error
import urllib.parse
import urllib.request
import concurrent.futures
from collections import defaultdict

API = "https://api.open.fec.gov/v1"
CYCLES = (2022, 2024, 2026)
THROTTLE = 1.25   # ~48/min, comfortably under FEC's 60/min even with retries
_last = [0.0]
_lock = threading.Lock()

# operator -> recipient_name variants (as they appear in FEC Schedule B)
OPERATORS = {
    "Zeitlin (convicted)": ["CLOUD DATA SERVICES", "LAV SERVICES",
                            "WIRED4DATA", "WIRED 4 DATA", "STANDARD DATA SERVICES"],
    "Daly (convicted)": ["BETTER MOUSETRAP DIGITAL", "REACH RIGHT DIGITAL"],
    "Gelvan (banned)": ["MARKET PROCESS GROUP", "OUTREACH CALLING",
                        "PUBLIC SUPPORT SERVICES"],
    "Olympic Media": ["OLYMPIC MEDIA"],
    "RetroMedia": ["RETROMEDIA"],
}


def get(path, retries=6, **params):
    params["api_key"] = os.environ.get("FEC_API_KEY", "DEMO_KEY")
    url = f"{API}/{path}?{urllib.parse.urlencode(params)}"
    for a in range(retries):
        # pace EVERY attempt (incl. retries) through the shared limiter, so a
        # burst of simultaneous 429 retries can't form a thundering herd.
        with _lock:
            gap = THROTTLE - (time.time() - _last[0])
            if gap > 0:
                time.sleep(gap)
            _last[0] = time.time()
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return {"results": [], "pagination": {}}
            if e.code in (429, 500, 502, 503) and a < retries - 1:
                time.sleep(3 * (a + 1)); continue
            raise
        except (urllib.error.URLError, TimeoutError, ConnectionError):
            if a < retries - 1:
                time.sleep(3 * (a + 1)); continue
            raise
    return {"results": [], "pagination": {}}


def payers_of(name, cycle, max_pages=None):
    """{committee_id: [amount, count]} for disbursements to `name` in cycle.

    max_pages caps pagination (results are sorted by -amount, so the top pages
    capture the largest client payments that dominate the dollar-share; used by
    the hidden-operator detector to bound cost on widely-used vendors)."""
    agg = defaultdict(lambda: [0.0, 0])
    seek = {}
    pages = 0
    while True:
        d = get("schedules/schedule_b/", recipient_name=name,
                two_year_transaction_period=cycle, per_page=100,
                sort="-disbursement_amount", **seek)
        res = d.get("results", [])
        for r in res:
            amt = r.get("disbursement_amount") or 0
            if amt <= 0:
                continue
            cid = r.get("committee_id")
            agg[cid][0] += amt
            agg[cid][1] += 1
        pages += 1
        idx = (d.get("pagination", {}).get("last_indexes") or {})
        if len(res) < 100 or not idx.get("last_index") or (max_pages and pages >= max_pages):
            break
        seek = {"last_index": idx["last_index"],
                "last_disbursement_amount": idx["last_disbursement_amount"]}
    return agg


def committee_name(cid):
    res = get(f"committee/{cid}/").get("results", [])
    return res[0].get("name") if res else ""


def main():
    key = "DEMO_KEY" if os.environ.get("FEC_API_KEY", "DEMO_KEY") == "DEMO_KEY" else "FEC_API_KEY"
    print(f"Vendor-back network map (key: {key}, cycles {CYCLES})\n")
    # operator -> committee_id -> [amount, count]
    networks = {op: defaultdict(lambda: [0.0, 0]) for op in OPERATORS}

    tasks = [(op, v, c) for op, vs in OPERATORS.items() for v in vs for c in CYCLES]

    def run(t):
        op, v, c = t
        return op, payers_of(v, c)

    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
        for op, agg in ex.map(run, tasks):
            for cid, (amt, cnt) in agg.items():
                networks[op][cid][0] += amt
                networks[op][cid][1] += cnt

    all_cids = {cid for net in networks.values() for cid in net}
    print(f"resolving {len(all_cids)} committee names ...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
        names = dict(zip(all_cids, ex.map(committee_name, all_cids)))

    summ, edges = [], []
    for op, net in networks.items():
        total = sum(a for a, _ in net.values())
        summ.append({"operator": op, "client_pacs": len(net),
                     "total_paid_2022_2026": round(total, 2)})
        for cid, (amt, cnt) in net.items():
            edges.append({"operator": op, "committee_id": cid,
                          "committee_name": names.get(cid, ""),
                          "amount": round(amt, 2), "transactions": cnt})

    summ.sort(key=lambda x: x["total_paid_2022_2026"], reverse=True)
    edges.sort(key=lambda x: (x["operator"], -x["amount"]))
    with open("vendor_networks.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["operator", "client_pacs", "total_paid_2022_2026"])
        w.writeheader(); w.writerows(summ)
    with open("vendor_network_clients.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["operator", "committee_id", "committee_name", "amount", "transactions"])
        w.writeheader(); w.writerows(edges)

    print("\n=== VENDOR-BACK NETWORKS (2022-2026) ===")
    for s in summ:
        print(f"\n{s['operator']}: {s['client_pacs']} client PACs, "
              f"${s['total_paid_2022_2026']:,.0f} total")
        top = sorted([e for e in edges if e["operator"] == s["operator"]],
                     key=lambda e: -e["amount"])[:6]
        for e in top:
            print(f"    ${e['amount']:>12,.0f}  {e['committee_id']}  {(e['committee_name'] or '')[:38]}")
    print("\n-> vendor_networks.csv, vendor_network_clients.csv")


if __name__ == "__main__":
    main()
