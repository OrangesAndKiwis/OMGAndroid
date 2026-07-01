"""Unsupervised hidden-operator detector — the generalized watchlist.

The watchlist only catches KNOWN convicted operators. This finds hidden ones with
no conviction, by scoring every fundraising vendor on the company it keeps:

  scam_concentration = $ from scam-profile PACs / $ from ALL its client committees

A vendor whose clientele is concentrated in scam-profile PACs (high small-dollar,
~0 to candidates) is a hidden operator — that is exactly what separated Zeitlin/
Gelvan (63-76%) from Daly/Olympic (2-5%). Also flags BESPOKE vendors (a vendor
that serves ~1 committee and takes most of its money = the operator's own shell).

Candidate vendors are DISCOVERED from the data (vendors paid by >=2 scam-profile
band PACs), not hardcoded. Scam-profile label = membership in case_candidates.csv.

    python hidden_operators.py

Writes hidden_operators.csv.
"""
import csv
import re
from collections import defaultdict

import vendor_back as vb   # reuse thread-safe FEC client + payers_of
import concurrent.futures

MIN_SHARED_PACS = 2
MIN_TOTAL = 50_000        # vendor must move real money to be worth flagging
TOP_CANDIDATES = 45       # cap the discovered vendor list (bounds API cost)

# payment processors / infra — never operators (reuse clustering stoplist idea)
STOP = ("WINRED", "ACTBLUE", "ANEDOT", "STRIPE", "PAYPAL", "SQUARE", "GOOGLE",
        "META", "FACEBOOK", "AMAZON", "NGP VAN", "GUSTO", "TATANGO", "USPS",
        "AMERICAN EXPRESS", "BANK", "AUTHORIZE", "PARAGON", "SWITCHBOARD",
        "SANDLER REIFF", "ELIAS LAW", "NATIONBUILDER", "COMPLIANCE", "CPA",
        "RALLYPAY", "PAYROLL", "MERCHANT")
# already-known operators (analyzed separately) — skip to find NEW ones
KNOWN = ("CLOUD DATA", "LAV SERVICES", "WIRED4DATA", "STANDARD DATA",
         "BETTER MOUSETRAP", "REACH RIGHT", "OLYMPIC MEDIA", "MARKET PROCESS",
         "OUTREACH CALLING", "RETROMEDIA")


def skip(v):
    return (not v or len(v) < 6 or any(s in v for s in STOP)
            or any(k in v for k in KNOWN))


def discover_candidates():
    """Vendors paid by >=MIN_SHARED_PACS scam-profile band PACs (from step-2 edges)."""
    scam = {r["committee_id"] for r in csv.DictReader(open("case_candidates.csv"))}
    vp = defaultdict(lambda: [0.0, set()])
    for r in csv.DictReader(open("pac_vendor_edges_full.csv")):
        if r["purpose"] not in ("fundraising", "consulting", "admin"):
            continue
        v = r["vendor_normalized"]
        if skip(v):
            continue
        vp[v][0] += float(r["amount"] or 0)
        vp[v][1].add(r["committee_id"])
    cands = [(v, amt, len(pacs)) for v, (amt, pacs) in vp.items()
             if len(pacs) >= MIN_SHARED_PACS]
    cands.sort(key=lambda x: -x[1])
    return scam, cands[:TOP_CANDIDATES]


def main():
    scam, cands = discover_candidates()
    print(f"Discovered {len(cands)} candidate vendors (paid by >= {MIN_SHARED_PACS} "
          f"scam-profile PACs). Running vendor-back on each ...\n")

    def analyze(item):
        vendor = item[0]
        clients = vb.payers_of(vendor, 2024)  # {cid: [amt, cnt]}
        total = sum(a for a, _ in clients.values())
        scam_amt = sum(a for cid, (a, _) in clients.items() if cid in scam)
        return {
            "vendor": vendor,
            "total_paid_2024": round(total, 2),
            "client_committees": len(clients),
            "scam_profile_clients": sum(1 for cid in clients if cid in scam),
            "scam_dollar_share_pct": round(scam_amt / total * 100, 1) if total else 0,
            "bespoke": len(clients) <= 2,
        }

    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
        rows = [r for r in ex.map(analyze, cands) if r["total_paid_2024"] >= MIN_TOTAL]

    # hidden-operator score: concentration weighted by volume; bespoke boosted
    for r in rows:
        conc = r["scam_dollar_share_pct"] / 100
        r["hidden_operator_score"] = round(
            conc * (1 + (0.3 if r["bespoke"] else 0)) *
            (min(r["total_paid_2024"], 5_000_000) / 5_000_000) ** 0.3, 3)
    rows.sort(key=lambda r: (r["scam_dollar_share_pct"], r["total_paid_2024"]),
              reverse=True)

    cols = ["vendor", "scam_dollar_share_pct", "scam_profile_clients",
            "client_committees", "total_paid_2024", "bespoke", "hidden_operator_score"]
    with open("hidden_operators.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)

    print(f"{'scam$%':>6} {'scamPACs':>8} {'clients':>7} {'total$':>12} {'bespoke':>7}  vendor")
    for r in rows[:30]:
        print(f"{r['scam_dollar_share_pct']:>5.0f}% {r['scam_profile_clients']:>8} "
              f"{r['client_committees']:>7} {r['total_paid_2024']:>12,.0f} "
              f"{'YES' if r['bespoke'] else '':>7}  {r['vendor'][:34]}")
    print(f"\n-> hidden_operators.csv  ({len(rows)} vendors scored)")


if __name__ == "__main__":
    main()
