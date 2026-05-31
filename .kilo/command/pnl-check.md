---
model: deepseek-obsidian/deepseek-v4-pro
description: "Monthly P&L cross-check: compare P&L wiki vs op-log weekly sums. Run day 10-16."
---

# /pnl-check - Monthly P&L Cross-Check
# v1.0 | 2026-05-31
# PURPOSE: Cross-check P&L actuals vs weekly operation log sums for revenue and COL%.
# CADENCE: Days 10-16 each month (separated from /lint v4.0)

## Usage
```
/pnl-check
```

## Steps

### 1. Check cadence
If today not between day 10-16 of current month -> skip.

### 2. Determine report period
Previous month (lint runs 12/06 -> check May).

### 3. Read P&L wiki files
PL_LU3_2026.md, PL_LU5_2026.md, PL_LU7_2026.md, PL_Target*.md
If missing target month -> flag warning and skip.

### 4. Read op logs for same period
01_Weekly_Revenue_Log.md, 07_COL_Weekly_Log.md

### 5. Cross-check
Revenue: P&L vs weekly sum (per store, ALL). Flag gap >5%.
Labour: COL% actual vs target.
Month-over-month: revenue change, COL% delta.

### 6. Save + commit