# Property Table Schema Reference

Complete YAML frontmatter schema for L'Usine log files.

## Required Fields

```yaml
name: "Log Name"                    # Human-readable log name
type: "tracker"                     # Fixed: "tracker"
status: "active"                    # Fixed: "active"
owner: "Warren (Head of Ops)"       # Fixed
stores: ["LU3", "LU5", "LU7"]       # Array of store codes
```

## Data Source Configuration

```yaml
data_source:
  sheet_id: "1ZtIocc_Ic1z-tO1JGd4ZLnRB_7ZHHkvpJ5emaWJyeEE"  # Google Sheet ID
  sheet_name: "TabName"             # Exact tab name in GSheet
  gid: "123456789"                  # GSheet GID (string)
  parser: "vault/10_OPERATION_DATA/parsers/parser_name.py"
  parser_version: "1.0"             # Semantic version
```

## Refresh & Cross-refs

```yaml
refresh_cadence: "Mon 09:45 (auto via Hermes cron)"
cross_refs:
  - "01_Weekly_Revenue_Log.md (context description)"
  - "04_LTO_Weekly_Log.md (LTO orders)"
  - "07_COL_Weekly_Log.md (Labor context)"
```

## Key Definitions (Metric Formulas)

```yaml
key_definitions:
  gross_revenue: "Net Sales after merchant discounts, before commission"
  commission: "Platform fee (negative in sheet, shown positive)"
  net_revenue: "gross_revenue * 0.882 (VAT 8%/10% + SC 5%)"
  actual_covers: "gross_covers - split_orders (real guest count)"
  rev_per_cover: "net_revenue / actual_covers (in k VND)"
```

## Targets (Thresholds for Flags)

```yaml
targets:
  commission_max_pct: 20.0
  commission_warn_pct: 18.0
  roas_min_x: 3.0
  roas_warn_x: 1.0
  rating_min: 4.0
  col_green_max: 15.0
  col_yellow_max: 20.0
  splh_green_min: 350000
  splh_yellow_min: 250000
  pass_rate_min_pct: 95
```

## Auto-synced Fields

These are automatically updated on every parser run:
```yaml
last_updated: "2026-06-16"          # Today's date
data_source.parser_version: "1.1"   # From parser constant
data_source.sheet_id: "..."         # From parser constant
data_source.gid: "..."              # From parser constant
```

## Example: Complete Frontmatter

```yaml
---
name: "GrabFood Weekly Tracker"
type: "tracker"
status: "active"
owner: "Warren (Head of Ops)"
stores:
  - LU3
  - LU5
data_source:
  sheet_id: "1ZtIocc_Ic1z-tO1JGd4ZLnRB_7ZHHkvpJ5emaWJyeEE"
  sheet_name: "Grabfood"
  gid: "689394201"
  parser: "vault/10_OPERATION_DATA/parsers/grabfood_parser.py"
  parser_version: "1.1"
refresh_cadence: "Mon 09:45 (auto via Hermes cron)"
cross_refs:
  - "01_Weekly_Revenue_Log.md (Revenue context)"
  - "04_LTO_Weekly_Log.md (LTO orders)"
  - "07_COL_Weekly_Log.md (Labor cost context)"
key_definitions:
  gross: "Net Sales (after merchant discounts, before commission)"
  commission: "Grab channel commission fee (negative in sheet, shown positive)"
  net_after_ad: "Net Payout - Ad Spend"
  roas: "Revenue on ad active days / Ad spend on those days"
targets:
  commission_max_pct: 20.0
  roas_min_x: 3.0
  rating_min: 4.0
last_updated: "2026-06-16"
---
```