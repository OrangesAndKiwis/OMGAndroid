"""Hidden-operator detector — OFFLINE variant (no FEC API calls).

Computes candidate hidden operators purely from data already on disk
(pac_vendor_edges_full.csv + case_candidates.csv), so it runs when the API is
rate-limited. It ranks fundraising/mail/list vendors by how many scam-profile
PACs they serve and the scam-$ share WITHIN THE ANALYZED BAND.

CAVEAT vs. hidden_operators.py: the denominator here is band clients only, not
ALL of a vendor's clients. So a "100%" means "100% of the *band* PACs paying it
are scam-profile" — a vendor may still serve mainstream committees outside the
band (as TMA Direct and Mothership Strategies do, which is why they show <50%).
Treat 100%-share, multi-scam-PAC, obscure-name vendors as CANDIDATES to confirm
with the full vendor-back sweep (hidden_operators.py) once the API resets.

    python hidden_operators_offline.py   ->  hidden_operators.csv
"""
import csv
from collections import defaultdict

STOP = ("WINRED", "ACTBLUE", "ANEDOT", "STRIPE", "PAYPAL", "GOOGLE", "META",
        "AMAZON", "NGP VAN", "GUSTO", "TATANGO", "USPS", "AMERICAN EXPRESS",
        "BANK", "AUTHORIZE", "PARAGON", "SWITCHBOARD", "SANDLER REIFF",
        "ELIAS LAW", "NATIONBUILDER", "COMPLIANCE", "CPA", "RALLYPAY",
        "PAYROLL", "MERCHANT")


def skip(v):
    return not v or len(v) < 6 or any(s in v for s in STOP)


def main():
    scam = {r["committee_id"] for r in csv.DictReader(open("case_candidates.csv"))}
    V = defaultdict(lambda: {"pacs": set(), "scam": set(), "scam_amt": 0.0, "amt": 0.0})
    for r in csv.DictReader(open("pac_vendor_edges_full.csv")):
        if r["purpose"] not in ("fundraising", "consulting", "admin"):
            continue
        v = r["vendor_normalized"]
        if skip(v):
            continue
        cid, amt = r["committee_id"], float(r["amount"] or 0)
        d = V[v]; d["pacs"].add(cid); d["amt"] += amt
        if cid in scam:
            d["scam"].add(cid); d["scam_amt"] += amt

    rows = []
    for v, d in V.items():
        if len(d["pacs"]) < 2:
            continue
        rows.append({
            "vendor": v,
            "scam_profile_clients": len(d["scam"]),
            "band_clients": len(d["pacs"]),
            "band_scam_dollar_share_pct": round(d["scam_amt"] / d["amt"] * 100, 1) if d["amt"] else 0,
            "scam_dollars_band": round(d["scam_amt"], 2),
            "bespoke": len(d["pacs"]) <= 2,
        })
    rows.sort(key=lambda r: (r["scam_profile_clients"], r["scam_dollars_band"]), reverse=True)

    with open("hidden_operators.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)

    print(f"{'scamPACs':>8} {'bandPACs':>8} {'scam$%':>7} {'scam$':>12}  vendor")
    for r in rows[:25]:
        bq = " [bespoke]" if r["bespoke"] else ""
        print(f"{r['scam_profile_clients']:>8} {r['band_clients']:>8} "
              f"{r['band_scam_dollar_share_pct']:>6.0f}% {r['scam_dollars_band']:>12,.0f}  "
              f"{r['vendor'][:30]}{bq}")
    print(f"\n-> hidden_operators.csv ({len(rows)} vendors)")


if __name__ == "__main__":
    main()
