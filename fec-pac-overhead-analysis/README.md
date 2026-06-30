# FEC PAC Overhead Analysis

Identifies PACs that spend less than 20% of their total spend on candidates, then
clusters those PACs by the vendors they share. Covers the 2024 and 2026 cycles
across all committee types, using the [OpenFEC API](https://api.open.fec.gov/developers/).

See [`CLAUDE.md`](./CLAUDE.md) for the analysis spec and conventions.

## Setup

1. `cp .env.example .env` and add your `FEC_API_KEY`.

## Outputs

| File | Description |
| --- | --- |
| `flagged_pacs.csv` | PACs with <20% of spend going to candidates (main output) |
| `vendor_clusters.csv` | Flagged PACs grouped by shared vendors |
| `top_vendors.csv` | Overhead vendor rankings |

## Notes

- `--limit 50` for test runs.
- `MIN_TOTAL_SPEND = $10k` noise filter.
- Animal Protection PAC (`C00526558`) is a good validation case.
