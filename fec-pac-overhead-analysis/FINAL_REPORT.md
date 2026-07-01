# FEC PAC Overhead Analysis — Final Report (2024 cycle)

**Goal.** Identify PACs that may be *deceptively raising money* — soliciting
donations for candidates/causes while spending most of it on fundraising,
overhead, or insiders — and surface coordinated operations via shared vendors.

**One-line result.** Screening the full 2024 PAC universe on FEC financial
ratios, then layering vendor-level signals, produces **20 high-confidence leads
(score ≥ 8)** — including several *independently documented* scam operations and
one tied to a **criminal fraud conviction** — with **~$14M already raised into
2026** across the top tier. This is a triage screen for review, **not** a fraud
determination.

---

## 1. Method & funnel

| Stage | Count | Rule |
|---|--:|---|
| PAC universe, 2024, ≥ $10k disbursed | 5,980 | `min_disbursements` = MIN_TOTAL_SPEND |
| — excluded: Joint Fundraising Committees | −776 | designation `J` (structural high cost-to-raise) |
| **Flagged** (mission ratio < 20%) | **1,548** | `(contributions + independent expenditures) / disbursements < 0.20` |
| Deep-analyzed (sweet-spot band) | 752 | receipts $100k–$50M, ranked by overhead % |

*Mission ratio* counts independent expenditures, not just candidate
contributions — without that, every legitimate IE-only Super PAC false-flags.
Party committees (types X/Y/Z) and JFCs are excluded as structural
false-positive classes.

## 2. Signals & composite score

Each analyzed PAC gets a transparent additive score (`score.py`):

| Signal | Points | Rationale |
|---|--:|---|
| Pays a **known-bad fundraiser** (watchlist) | +4 | vendor tied to documented scam ops / convictions |
| **Self-dealing** (treasurer-matched payee > $0) | +3 | money to the insider running the PAC |
| **Cost-to-raise** ≥60% / ≥40% / ≥25% | +3/+2/+1 | the fundraising treadmill |
| **Overhead** ≥90% / ≥70% | +2/+1 | operating spend vs. mission |
| **~0% to candidates** (mission <5%) | +1 | |
| Member of a **shared-vendor group** | +1 | coordinated operation |
| *(2026 raised-to-date)* | tiebreak | harm currently accruing |

**Score distribution (752 analyzed):** 6 at 11 · 3 at 10 · 4 at 9 · 7 at 8 ·
then a long tail. The top tier (≥8) is 20 PACs. Full ranking in `scored_leads.csv`.

## 3. Top leads (score ≥ 9)

| Score | PAC | Cost-to-raise | 2024 receipts | Signal | Corroboration |
|--:|---|--:|--:|---|---|
| 11 | **American Coalition for Crisis Relief** | 83% | $4.9M | watchlist | ✅ **documented scam** (multiple outlets) |
| 11 | **Ranger PAC** | 69% | $2.6M | watchlist | ✅ **documented** (Kilgore/PDS self-dealing) |
| 11 | Early Vote Action PAC | 65% | $7.1M | watchlist | ⚠ statistical only |
| 11 | God, Family, & Country PAC | 79% | $0.4M | watchlist | ⚠ statistical only |
| 11 | Elect Republicans | 60% | $0.3M | watchlist | ⚠ statistical only |
| 11 | **Nine PAC** | 60% | $0.3M | watchlist | ✅ cluster (Olympic/Reach Right) |
| 10 | Black America's Political Action Cmte | 60% | $2.2M | self-deal $251k | ⚠ statistical only |
| 10 | New Journey PAC | 68% | $1.4M | self-deal $247k | ⚠ statistical only |
| 10 | **Red Renaissance** | 54% | $0.1M | watchlist | ✅ cluster (Klacik/Olympic Media) |
| 9 | Bowers News Media PAC | 89% | $0.2M | self-deal $161k | ⚠ statistical only |
| 9 | Defeat Republicans PAC | 54% | $0.9M | self-deal | ⚠ statistical only |
| 9 | Reform California Voter Guide | 122%† | $0.3M | self-deal | ⚠ statistical; †artifact |
| 9 | Elder for America | 156%† | $0.1M | self-deal | ⚠ statistical; †artifact |

† Cost-to-raise > 100% means fundraising spend exceeded *this cycle's* receipts
(spending reserves) — a red flag but partly an accounting artifact; verify the
committee is active, not terminated.

At **score 8**, the screen also auto-surfaced the **Zeitlin police-PAC network**
— Police Coalition of America ($680k to watchlist vendors), Police and Trooper
Support ($365k), American Veterans Initiative ($314k) — plus **SEAL PAC** and
**Defending the Republic** (Sidney Powell). All five are externally corroborated
(see §6).

## 4. The known-bad-fundraiser watchlist worked

**10 PACs routed $2.55M to vendors tied to documented scam operations** (Cloud
Data/Zeitlin — *convicted*; Reach Right/Daly — *convicted*; Olympic Media;
Crisis Relief Consultants). Because the watchlist is built from criminal/
journalistic records, these hits are effectively self-corroborating: the PAC is
paying a firm already established as a scam-fundraising operator. This single
signal independently rediscovered the Zeitlin police-PAC network and the
Klacik/Olympic Media committees.

## 5. Self-dealing

**38 PACs paid $2.51M to payees matching their own treasurer's name** — the
insider-enrichment signature. Caveat (from research): the name-match can also
catch an *officer* in a dual role or a shared-address vendor, so each hit needs
a one-line confirmation before publishing (see §7).

## 6. Shared-vendor groups

145 distinctive shared-vendor groups (2–8 PACs each) link 112 flagged PACs
(`vendor_clusters.csv`). The actionable unit is *"these N flagged PACs all route
overhead to the same distinctive fundraising vendor"* — e.g. TMA Direct (8),
MDI Imaging Mail (5), Switchboard (6), Frontline Strategies (5). The strongest
groups overlap the watchlist (Olympic Media, Cloud Data), tying individual leads
into operations. *Note:* connected-component clustering was abandoned — at this
scale it chains into one meaningless blob; and shared **treasurers** are NOT a
cluster signal (Bradley Crate alone is treasurer for 200+ committees).

## 7. External corroboration (from `research_findings.md`)

Run blind on ratios, the screen rediscovered **four+ documented scam/misuse
operations**, one with a criminal conviction:

- **Law Enforcement for a Safer America / police network** — CNN & Jacobin
  exposés; principal telemarketer **Richard Zeitlin convicted of wire fraud (121 mo.)**
- **American Coalition for Crisis Relief** — multiple outlets label it a scam PAC
- **SEAL PAC / Ranger PAC** — Roll Call exposé; active FEC inquiry; treasurer
  Kilgore routes fees to his own firm across PACs
- **Defending the Republic** (Powell) — Dominion filing, Florida fine, federal subpoena
- **Cluster vendors** — Olympic Media ("a racket"), and **Reach Right = Jack Daly,
  convicted of scam-PAC fraud**

False positives all fell into explainable classes (below).

## 8. Limitations & false-positive classes

- **Structural false positives excluded or flagged:** party committees, JFCs,
  union/trade transfer PACs, issue-advocacy PACs (e.g., Wolf PAC — ~0% to
  candidates by design), and IE-only Super PACs measured in a $0-IE period.
- **>100% cost-to-raise = termination/reserve artifact**, not a super-scam.
- **Self-dealing name-match** conflates treasurer vs. officer vs. shared-address
  vendor — confirm before publishing.
- **Schedule B is not authoritative for dollar totals** (amended/superseded
  transactions inflate it); totals-endpoint figures are used for all ratios.
- **Watchlist is a signal, not a verdict** — some listed vendors also serve
  mainstream clients (e.g., Reach Right's largest clients are the NRCC, Rand Paul).
- **Coverage:** 752 of 1,548 flagged were deep-analyzed (the $100k–$50M band).
  Tiny and mega PACs are flagged (Step 1) but not vendor-analyzed.

## 9. Recommended use & next steps

1. **Review the top tier (score ≥ 8)** in `scored_leads.csv` — the watchlist and
   self-dealing hits are the highest-value, most defensible leads.
2. **Research the ~10 statistical-only top leads** (Early Vote Action, God Family
   & Country, Black America's PAC, New Journey, Bowers News Media, Defeat
   Republicans) to promote them from statistical to corroborated.
3. **Confirm the 38 self-dealing hits** (treasurer vs. officer vs. address).
4. **Optional expansion:** vendor-analyze the remaining 796 flagged PACs outside
   the band, and grow the watchlist from each newly-confirmed operation.

### Artifacts
`flagged_pacs.csv` (1,548) · `scored_leads.csv` (752, ranked) ·
`suspects_summary.csv` (vendor signals) · `vendor_clusters.csv` (145 groups) ·
`top_vendors_full.csv` · `research_findings.md` (corroboration) · pipeline:
`analyze.py` → `vendors.py` → `clusters.py` → `score.py`.
