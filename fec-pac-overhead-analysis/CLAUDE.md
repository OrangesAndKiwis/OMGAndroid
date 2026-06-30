# FEC PAC Overhead Analysis

Goal: Identify PACs where <20% of spend goes to candidates, cluster by shared vendors.
Cycles: 2024, 2026. All committee types.
API key: stored in .env as FEC_API_KEY

## Outputs
- flagged_pacs.csv — main output
- vendor_clusters.csv — PAC groups by shared vendors
- top_vendors.csv — overhead vendor rankings

## Notes
- Use --limit 50 for test runs
- MIN_TOTAL_SPEND = $10k (noise filter)
- Animal Protection PAC is a good validation case (C00526558)
