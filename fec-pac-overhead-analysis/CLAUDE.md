# FEC PAC Overhead Analysis

Goal: Find PACs that may be deceptively raising money — soliciting donations
ostensibly for candidates/causes while spending little on that mission and most
on overhead (fundraising vendors, consultants, insiders). Cluster by shared
vendors to surface coordinated operations.

API key: stored in .env as FEC_API_KEY

## Methodology (decisions locked during validation spikes)

- **Flagging basis: 2024 (last completed cycle).** 2026 is mid-cycle and
  back-loaded, so it is NOT used to judge — it is reported as a
  `raised_2026_to_date` exposure column only.
- **Metric = mission ratio**, not contributions-only:
  `(fed_candidate_committee_contributions + independent_expenditures) / disbursements < 0.20`.
  Counting IEs is required so legitimate independent-expenditure Super PACs are
  not all false-flagged (validated: Senate Leadership Fund clears at ~94%
  mission; status-quo contributions-only wrongly put it at 23%).
- **Exclude false-positive classes** that have high cost-to-raise / low mission
  ratio for legitimate structural reasons (found during the full run):
  - **Party committees** (types X/Y/Z) — spend via coordinated expenditures/transfers.
  - **Joint Fundraising Committees** (designation `J`) — raise jointly then transfer
    out (e.g. RUBIO VICTORY COMMITTEE, TEAM SCALISE). Excluded in analyze.py.
  - **Union/trade transfer PACs** — money leaves as transfers to affiliated PACs.
  Real scams are typically designation `U` (non-connected), e.g. LAW ENFORCEMENT
  FOR A SAFER AMERICA, SEAL PAC.
- **Target the scam sweet spot for deep analysis**: rank by overhead PERCENTAGE
  within a receipts band ($100k–$50M). Billion-dollar committees have low
  overhead % (legit scale) and over-cluster on ubiquitous vendors (Google,
  ActBlue); tiny union locals are noise.
- **Cluster on distinctive vendors only**: drop vendors used by >30% of the
  analyzed PACs — ubiquitous vendors link everyone into one meaningless blob.
- **Overhead ratio** (`operating_expenditures / disbursements`) is a secondary
  corroborating signal, not the primary gate (it can't separate the validation
  case at 70% from legit DCCC at 58%).

## Stronger signals to add (vendor layer = the real detector)

- **Cost-to-raise-a-dollar**: fundraising-purpose Schedule B spend / receipts.
  More direct than the candidate ratio for treadmill scams.
- **Related-party / self-dealing**: match Schedule B payee name/address against
  the committee's own `treasurer_name` + address. Closes the main evasion
  (overhead disguised as IEs paid to a captive firm). Caveat: shared-office
  addresses (e.g. 122 C St NW) cause false merges — normalize carefully.
- **Operation-level clustering**: rank vendor clusters by
  (# flagged PACs sharing vendor) × (aggregate overhead $), and cross-reference
  shared treasurers across committees — that finds the operation, not the symptom.
- **Lead score, not a hard cutoff**: combine low mission ratio + high
  cost-to-raise + related-party hit + cluster membership; review the ranked tail.

Output is *leads for review*, not fraud accusations — high overhead is legal.

## Pipeline (built & tested)

1. `analyze.py`  — bulk 2024 sweep -> `flagged_pacs.csv` (+ 2026 raised-to-date).
2. `vendors.py`  — Schedule B per flagged PAC -> `top_vendors.csv` + `pac_vendor_edges.csv`
   (cost-to-raise, related-party self-dealing, vendor rollup).
3. `clusters.py` — groups PACs by shared overhead vendors -> `vendor_clusters.csv`.

Helpers: `validate.py` (single-PAC check), `compare.py` (ratio comparison).

## Data-quality caveats (found during build)

- **Schedule B is NOT authoritative for dollar totals.** Its sums exceed the
  committee's reported disbursements because the API returns superseded
  transactions from amended filings (and Schedule B only itemizes payments
  >$200). Use the totals endpoint for magnitudes; use Schedule B only for
  vendor identification and relative allocation. Cost-to-raise therefore uses
  authoritative `receipts` from totals as the denominator.
- **Negative disbursements** (refunds/corrections) must be summed (not skipped)
  so they net out — skipping them inflates vendor totals.
- **Use FEC seek pagination** (`last_index`), not page numbers — page-based
  paging duplicates/skips rows on sorted Schedule B queries.
- **Cost-to-raise is the key discriminator** validated in testing: it separates
  transfer-heavy union/trade PACs (~0%) from fundraising-treadmill PACs (50%+),
  which the mission ratio alone cannot.

## Outputs
- flagged_pacs.csv — main output
- vendor_clusters.csv — PAC groups by shared vendors
- top_vendors.csv — overhead vendor rankings

## Notes
- Use --limit 50 for test runs
- MIN_TOTAL_SPEND = $10k (noise filter)
- Animal Protection PAC is a good validation case (C00878165, Hybrid PAC, active 2024 & 2026).
  Validated: 6.6% candidate share in 2024, 3.3% in 2026 — both flagged.
  (Note: the ID C00526558 is NOT this PAC — it's a defunct, empty Super PAC.)
