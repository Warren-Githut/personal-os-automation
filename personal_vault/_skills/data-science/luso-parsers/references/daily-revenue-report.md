# Daily Revenue Report (`generate_today_revenue.py`)

**Location:** `vault/scripts/generate_today_revenue.py`  
**Schedule:** Daily 09:30 via cron  
**Output:** `vault/today.md` — WTD Revenue + COL table for LU3/LU5/LU7  
**Telegram delivery:** sends `today.md` as a document (see Known Issues)

## Data Source

Same GSheet as the COL Weekly parser:
- **Sheet ID:** `1ZtIocc_Ic1z-tO1JGd4ZLnRB_7ZHHkvpJ5emaWJyeEE`
- **GID:** `1732633441` — `COL_Weekly` tab
- **API:** Google Visualization (gviz) — same `fetch_gviz()` pattern used by all parsers

## What It Computes

| Section | Detail |
|---------|--------|
| Today WTD table | WTD Revenue, LW Revenue, Δ% per store + latest day COL/SPLH vs same weekday last week |
| Week-on-Week | Full week roll-up: Rev, Hours, COL%, SPLH vs LW, Pass Days |
| Month-on-Month | June vs May: Rev, Hours, COL%, SPLH, Pass Days |
| Open Cases | Reads `_cases/ACTIVE_CASES_INDEX.md` for active cases |

## Key Formulas (same as `07_COL_Weekly_Log`)

- **Net Revenue = Gross × 0.882** (VAT 8%/10% + Service Charge 5%)
- **SPLH = Net Revenue / Hours**
- **COL% = COL / Revenue** (from GSheet data)

## Relationship to Parser Infrastructure

- Uses the same `gviz` fetch + `col_map` pattern as `col_weekly_parser.py` and the other 8 parsers
- Reads from the same `COL_Weekly` GSheet tab that the COL parser writes to
- The revenue/WTD calculations are derived from COL_Weekly data, NOT from `01_Weekly_Revenue_Log`
- Runs independently of the Monday parser pipeline — it's a daily cron, not weekly

## Known Issues & Pitfalls

### 1. Monday Morning Data Gap

**Symptom:** At 09:30 Monday, `Current week rows: 0` — the script fetches zero rows for the current week.

**Root cause:** The `COL_Weekly` sheet is populated AFTER Monday's COL calculation, which hasn't happened yet at 09:30. Last week's data (W-1) IS available, but the current week (W0) has zero rows.

**Impact on WoW table:** Comparing 0tr rev against last week's actual revenue produces misleading `-100.00%` deltas for all three stores. The MoM table (June vs May) IS accurate because it reads historical data.

**Detection flag:** If `len(current_rows) == 0`, the WoW table is garbage. The script should ideally suppress WoW output or show a warning banner.

### 2. Telegram Delivery Never Works (Config Gap)

**Symptom:** Script prints `WARNING: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not set.` and skips send. This warning appears on EVERY run since the script was created.

**Root cause:** The script's `load_env()` reads `Warren_OS_Local/.env` (REPO_ROOT), but:
- `Warren_OS_Local/.env` does not exist
- `vault/.env` exists but contains only `GOOGLE_SA_CREDENTIALS` + `SLACK_WEBHOOK_URL` — no Telegram vars
- `~/.env` exists but also has no Telegram vars
- `TELEGRAM_CHAT_ID` is simply not configured anywhere

**Fix needed:** Either:
- Add `TELEGRAM_CHAT_ID=<actual_chat_id>` to one of the `.env` files
- Or refactor the script to use Hermes gateway Telegram channel instead of raw Bot API
- The `TELEGRAM_BOT_TOKEN` IS set in the environment (detected as `***set`), but without `TELEGRAM_CHAT_ID` it's useless

### 3. `today.md` Does Not Use Standard Frontmatter

The output file `vault/today.md` has no YAML frontmatter. It's purely a display artifact, not a log entry. This is intentional — it gets overwritten daily and is not meant to be part of the OPERATION_INDEX. But this means `ops-index-watchdog` should exclude it (it already does).

## Headless Execution

```bash
cd C:/Users/khoans/Documents/Warren_OS_Local
python vault/scripts/generate_today_revenue.py
```

Env vars required for Telegram send:
- `TELEGRAM_BOT_TOKEN` (IS set in environment)
- `TELEGRAM_CHAT_ID` (NOT configured — known issue)

The script's `load_env()` reads `Warren_OS_Local/.env` as fallback (this file doesn't exist as of June 2026).
