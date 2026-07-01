"""FEC PAC Overhead Analysis — composite lead scoring.

Joins step-1 flags (flagged_pacs.csv) with step-2 vendor signals
(suspects_summary.csv) and the clusters (vendor_clusters.csv) into a single
ranked lead score, so the final report ranks by one number instead of several
separate signals.

Scoring is additive and transparent (see WEIGHTS). It is a *triage* score for
review, not a fraud determination.

    python score.py            # writes scored_leads.csv

Signals (higher = more scam-like):
    cost_to_raise   fundraising spend / receipts   (the treadmill)
    overhead        operating_exp / disbursements
    self_dealing    treasurer-matched payee spend > 0
    watchlist       spend to a known-bad fundraiser > 0  (strongest)
    mission         (contributions + IEs) / disbursements  (low = worse)
    cluster         member of a shared-distinctive-vendor cluster
    exposure        2026 raised-to-date (harm currently accruing; tiebreak)
"""
import csv
import math


def num(r, k):
    try:
        return float(r.get(k) or 0)
    except (ValueError, AttributeError):
        return 0.0


def load(path, key="committee_id"):
    try:
        return {r[key]: r for r in csv.DictReader(open(path))}
    except FileNotFoundError:
        return {}


def cluster_members(path="vendor_clusters.csv"):
    """cid -> a shared-vendor group id it belongs to (any, for the score flag)."""
    members = {}
    try:
        for r in csv.DictReader(open(path)):
            gid = r.get("group_id") or r.get("cluster_id")
            for cid in (r.get("committee_ids") or "").split("; "):
                members.setdefault(cid.strip(), gid)
    except FileNotFoundError:
        pass
    return members


def score_row(flag, sus, in_cluster):
    ctr = num(sus, "cost_to_raise_pct")
    overhead = num(flag, "overhead_pct")
    mission = num(flag, "mission_pct")
    pts, why = 0, []

    if num(sus, "watchlist_vendor_spend") > 0:
        pts += 4; why.append("known-bad vendor")
    if num(sus, "related_party_spend") > 0:
        pts += 3; why.append("self-dealing")
    if ctr >= 60:
        pts += 3; why.append(f"cost-to-raise {ctr:.0f}%")
    elif ctr >= 40:
        pts += 2; why.append(f"cost-to-raise {ctr:.0f}%")
    elif ctr >= 25:
        pts += 1; why.append(f"cost-to-raise {ctr:.0f}%")
    if overhead >= 90:
        pts += 2; why.append(f"overhead {overhead:.0f}%")
    elif overhead >= 70:
        pts += 1; why.append(f"overhead {overhead:.0f}%")
    if 0 <= mission < 5:
        pts += 1; why.append("~0% to candidates")
    if in_cluster:
        pts += 1; why.append(f"cluster {in_cluster}")
    return pts, "; ".join(why)


def main():
    flags = load("flagged_pacs.csv")
    suspects = load("suspects_summary.csv")
    clusters = cluster_members()

    rows = []
    for cid, sus in suspects.items():   # only PACs with vendor analysis
        flag = flags.get(cid, {})
        pts, why = score_row(flag, sus, clusters.get(cid))
        rows.append({
            "score": pts,
            "committee_id": cid,
            "name": flag.get("name", ""),
            "designation": flag.get("designation", ""),
            "receipts_2024": num(sus, "receipts_2024"),
            "cost_to_raise_pct": num(sus, "cost_to_raise_pct"),
            "overhead_pct": num(flag, "overhead_pct"),
            "mission_pct": num(flag, "mission_pct"),
            "self_dealing_spend": num(sus, "related_party_spend"),
            "watchlist_vendor_spend": num(sus, "watchlist_vendor_spend"),
            "cluster_id": clusters.get(cid, ""),
            "raised_2026_to_date": num(sus, "raised_2026_to_date"),
            "treasurer": sus.get("treasurer", ""),
            "reasons": why,
        })

    # rank by score, then by exposure (2026 raised) as harm tiebreak
    rows.sort(key=lambda r: (r["score"], math.log10(r["raised_2026_to_date"] + 1)),
              reverse=True)

    cols = list(rows[0].keys()) if rows else []
    with open("scored_leads.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)

    print(f"Scored {len(rows)} leads -> scored_leads.csv\n")
    print(f"{'score':>5} {'ctr%':>5} {'oh%':>5} {'self-deal':>10} "
          f"{'watchlist':>10} {'receipts':>12}  name")
    for r in rows[:25]:
        print(f"{r['score']:>5} {r['cost_to_raise_pct']:>5.0f} {r['overhead_pct']:>5.0f} "
              f"{r['self_dealing_spend']:>10,.0f} {r['watchlist_vendor_spend']:>10,.0f} "
              f"{r['receipts_2024']:>12,.0f}  {(r['name'] or '')[:34]}")


if __name__ == "__main__":
    main()
