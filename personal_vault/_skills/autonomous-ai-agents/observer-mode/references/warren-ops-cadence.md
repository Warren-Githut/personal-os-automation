# Warren's Ops Cadence (Domain 2)

## Weekly Rhythm
- **Mon 10am**: Morning brief + context update (weekly themes → CONTEXT.md Section 5)
- **Mon/Wed/Fri 10am**: Morning brief (delta: COL, revenue, reviews, Kanban, calendar, tasks)
- **Sun 8pm**: Weekly connections (cross-domain patterns) + vault lint (data quality scan)

## Monthly Rhythm
- ~10th: CFO P&L → ingest to wiki/P&L_Budget/
- ~10th: Supplier COGS invoices → cross-ref Recipe_Index.json → Cost_Impact_Report.md

## On-Demand Commands
| Command | Purpose |
|---------|---------|
| `/ops-process-notes` | Fetch Slack brain-dumps, classify, route to journal/tasks/cases |
| `/ops-process-logs` | Drop weekly log files → auto-parse → append to logs |
| `/explore` | Filter new ideas before building (GO/NO-GO verdict) |
| `/ops-deep-research` | Full vault scan → beliefs, contradictions, gaps, questions |
| `/ops-cases` | Manage active cases |
| `/ops-query` | Search vault by keyword |

## Weekly Data Sources
| Source | Destination |
|--------|-------------|
| Revenue screenshot | 01_Weekly_Revenue_Log.md |
| HR Movement Report | 02_HR_Weekly_Log.md |
| COGS (monthly) | 03_COGS_Supplier_Monthly_Log.md |
| LTO tracker | 04_LTO_Weekly_Log.md |
| Google Reviews | 05_Google_Review_Weekly_Log.md |
| GrabFood | 06_GrabFood_Weekly_Log.md |
| COL / Working hours | 07_COL_Weekly_Log.md |

## Automations
- Morning brief: daily 10am GMT+7 (GitHub Actions) → Slack DM + vault log
- Weekly lint: Sun 8pm GMT+7 → data quality report
- Context update: Mon 7am reminder → Warren triggers manually

## Training Integration
ORION's morning brief Step 9 checks `hermes_training_log.md` daily and suggests the next training file. Visible in Warren's morning brief output.
