# Parser Canonical Location Decision — 2026-06-14

## Decision
**Canonical parser location: `vault/10_OPERATION_DATA/parsers/`**

## Duplicate Files Archived
Moved from `vault/scripts/` → `vault/scripts/.archive/duplicate_parsers_2026-06-14/`:
- `col_weekly_parser.py` (19.7 KB)
- `google_review_parser.py` (24.5 KB)
- `grabfood_parser.py` (27.2 KB)

## Rationale
1. **Single source of truth** — parsers live with the data they parse (same directory level as logs)
2. **Process-logs command contract** — registry table in `/ops-process-logs.md` Step 1 references files by name; having parsers in `10_OPERATION_DATA/parsers/` matches this mental model
3. **No import ambiguity** — scripts in `vault/scripts/` can import from `../10_OPERATION_DATA/parsers/` explicitly
4. **Archival follows safety protocol** — `git mv` to dated folder, single commit, instant rollback via `git mv back`

## Active Parsers (Canonical)
| Parser | Purpose | Called By |
|--------|---------|-----------|
| `cogs_parser.py` | COGS monthly log | `/process-logs` COGS step |
| `col_weekly_parser.py` | COL weekly log | `/process-logs` COL step |
| `google_review_parser.py` | Google reviews weekly | `/process-logs` Reviews step |
| `grabfood_parser.py` | GrabFood weekly | `/process-logs` GrabFood step |
| `payroll_cph.py` | Payroll CPH calc | `/process-logs` CPH step |
| `revenue_screenshot_parser.py` | Revenue screenshots | Manual/ops-ingest |

## Files That Import Parsers
- `vault/scripts/col_daily_fetch.py` → imports from `10_OPERATION_DATA.parsers`
- `vault/scripts/hr_ingest_auto.py` → imports from `10_OPERATION_DATA.parsers`
- `vault/scripts/monthly_aggregation.py` → imports from `10_OPERATION_DATA.parsers`

## Rollback (if needed)
```bash
git mv vault/scripts/.archive/duplicate_parsers_2026-06-14/col_weekly_parser.py vault/scripts/col_weekly_parser.py
git mv vault/scripts/.archive/duplicate_parsers_2026-06-14/google_review_parser.py vault/scripts/google_review_parser.py
git mv vault/scripts/.archive/duplicate_parsers_2026-06-14/grabfood_parser.py vault/scripts/grabfood_parser.py
```

## References
- Vault Ops Automation skill → Pitfall #3: "Duplicate parser locations"
- Vault Script Archival skill → workflow used for this move