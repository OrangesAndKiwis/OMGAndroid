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
- **Exclude party committees** (types X/Y/Z). They spend via coordinated
  expenditures and transfers, registering as neither contributions nor IEs —
  a false-positive class (e.g. DCCC looks scammy on raw ratios but is legit).
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
