---
name: luso-parsers
description: Run, patch, and maintain the L'Usine vault parser pipeline in .kilo/skills. Covers headless execution, shared config, log update helpers, and safe Python patching patterns.
version: 1.1
triggers:
  - run parser
  - dry run parser
  - patch parser
  - headless parse
  - .kilo/skills
  - hr_movements_parser
  - payroll_cph
  - payroll_cph_robust
  - cph
  - ops-cph
  - cph_result
  - col_weekly_parser
  - cogs_parser
  - grabfood_parser
  - google_review_parser
  - hourly_cover_parser
  - item_sales_weekly_parser
  - lto_weekly_parser
  - menu_gp_parser
  - wastage_parse_gen
  - cogs-ingest
  - cogs-report
  - cogs-gen
---

# L'Usine Parser Pipeline

Use when running, debugging, or refactoring any parser in the stable parser tree:
`C:/Users/khoans/Documents/Warren_OS_Local/vault/10_OPERATION_DATA/parsers/`.

`.kilo/skills/` still exists as the Hermes-managed source of truth for the original
template files. Apply fixes there first, then `cp` into `vault/10_OPERATION_DATA/parsers/`
so the vault copy is the one ops consumers actually run.

## Parser Inventory
See `references/parsers_inventory.md`.

## Headless Execution
```bash
cd C:/Users/khoans/Documents/Warren_OS_Local/vault/10_OPERATION_DATA/parsers
LUSINE_HEADLESS=1 LUSINE_FORCE=1 python <parser>.py <input>
```
- For `.kilo/skills/` template test runs, use `Python312/python.exe` if liteparse is installed there.
- **Run all parsers headless by default.** Set `LUSINE_HEADLESS=1` in every parser invocation so `_ask()` auto-returns the default and never blocks.
- **Force yes by default too:** add `LUSINE_FORCE=1` so log writes always proceed without confirmation.
- Do NOT leave raw `input()` or `_ask()` in any parser intended for automated runs. After patching: `grep -n 'input(' <parser>.py || true` and `grep -n '_ask(' <parser>.py || true` must return nothing.

## Shared Config Rule
- `cph_config.py` is the single source of truth for `SEGMENTS_ORDER`, `CPH_BENCHMARKS`, `SEGMENT_MAP`, `NON_COST_COLS`.
- Parsers must `from cph_config import ...`. Do not duplicate these dicts locally.

## Revenue Screenshot Parser — liteparse Drift + OCR Recovery (2026-07-13)

`revenue_screenshot_parser.py` OCRs 4 Power BI screenshots (sys/LU3/LU5/LU7) via liteparse, then merges + runs `verify_gate` (sum 3 stores == SYS; avg = net÷covers cross-check; party-size consistency).

**P1 — `liteparse.parse()` API removed (v2.5.1).** The parser does `import liteparse; liteparse.parse(img)`. Python `liteparse` 2.5.1 has NO `parse` attr (now `LiteParse` class via PyO3). Result: `AttributeError: module 'liteparse' has no attribute 'parse'`.
- **FIXED (2026-07-13):** `ocr_image()` now calls the **npm liteparse CLI** as primary (`liteparse parse <img> -o <out>`, native `C:/Users/...` path) with a **python `liteparse.LiteParse(ocr_enabled=True).parse(path)` fallback** (liteparse skill HARD GATE). The removed `liteparse.parse(img)` call is gone. Bypass via `--test-json` still works if both OCR paths fail. Warren explicitly wanted liteparse KEPT (not replaced by a raw npm wrapper), so the parser wraps liteparse, not bypasses it. If `ocr_image()` regresses to `liteparse.parse(...)`, it WILL fail on v2.5.1 — re-apply this fix.

**P2 — Windows PYTHONPATH + native path gotcha.** Parsers import `_frontmatter` / `_utils` from `10_OPERATION_DATA/scripts/modules`. The Windows `python3` does NOT resolve MSYS `/c/Users/...` paths (becomes `C:\c\Users\...`).
- **Correct invocation (verified 2026-07-13):**
  ```bash
  cd C:/Users/khoans/Documents/Warren_OS_Local/vault/10_OPERATION_DATA/scripts/modules
  export PATH="/c/Users/khoans/AppData/Roaming/npm:$PATH"   # so shutil.which("liteparse") finds the npm CLI
  PYTHONPATH="C:/Users/khoans/Documents/Warren_OS_Local/vault/10_OPERATION_DATA/scripts/modules" \
  LUSINE_HEADLESS=1 python3 "C:/Users/khoans/Documents/Warren_OS_Local/vault/10_OPERATION_DATA/parsers/<parser>.py" [args]
  ```
  Use `C:/Users/...` (forward slashes OK) everywhere — never `/c/Users/...` when invoking python3 OR passing image paths to liteparse (node binary can't expand MSYS).
- `liteparse` npm CLI also needs native `C:/Users/...` paths. See liteparse skill for the canonical OCR gate + the `LiteParse` python-class fallback.

**P5 — OCR line-merge pitfall (Power BI value+label rows collapse into ONE physical line).**
The BI "Full Week" card renders as: `643,954,164  2,380  270,569  1,909  0%` on line N, then `NET REVENUE  COVERS  AVG SPEND/COVER  TICKETS  DAILY TARGET ACHIEVED` on line N+1. The OLD `revenue_screenshot_parser.py` searched for the label then read *forward* 200 chars (landing in the NEXT block's date) → returns None. Worse, the npm CLI often **merges value+label onto one physical line** (`...643,954,164 2,380 270,569 1,909 0%.NET REVENUE COVERS...`), so "COVERS" sits on the SAME line as "NET REVENUE" and there is no separate "line above" at all.
- **Robust fix (shipped 2026-07-13):** locate the `NET REVENUE`/`Doanh thu` label, then grab the **4 numbers immediately preceding it on the same (merged) line** — take `nums[:4]` of the row that starts with the biggest number (net revenue is the largest). Column order is fixed: `[net_rev, covers, avg, tickets]`; drop any trailing target% via `nums[:4]`. For W/W% blocks, walk UP to the nearest non-empty line and take its pct token.
  - Do NOT assume value-row-above-label. OCR merge order is unpredictable; anchor on the label and take the numbers *before* it.
- **Store OCR column-shift recovery** (see P3) still applies: LU3 covers can OCR as `266,211` (actually `876`); the verify_gate party-size/sum check (P4) is the intended SIGNAL — fix via SYS−other2, never silence it.
- **Verify after any OCR-parse change:** run the real image path (`--sys/--lu3/--lu5/--lu7`) through liteparse CLI + `parse_one_bi`, then assert SYS/LU5/LU7 net_rev/covers match known values AND `verify_gate` returns `ok=False` on the LU3 bad-OCR input (exit-2 behavior intact). Temp `hermes-verify-*.py` in `%TEMP%`.
- **WARREN CORRECTION (2026-07-13) — Revenue SSOT block order + MTD/YTD MUST be filled:** When building/ingesting a week into `01_SSOT_01_Weekly_Revenue_Log.md`:
  1. **LATEST WEEK ON TOP** (newest-on-top), never leave the new week at the bottom. `revenue_screenshot_parser.py` now does this itself: after reading the SSOT, it finds the first `\n## 20` block and **prepends** the new block before it (inserting at the top, after frontmatter + Monthly Targets + dash link). The OLD code appended at EOF → W28 landed at the bottom, which Warren caught. If you ever hand-edit or write a sibling parser, prepend, don't append. Use `insert_or_replace_weekly()` (in `_utils.py`) where available.
  2. **Fix ISO week label** from the block's start date (`datetime.isocalendar()` → `YYYY-Www`). The Power BI source mislabels 06-29→07-05 as "W29" — it is actually **2026-W27**. When adding/relabeling, derive the label from the date, never trust the BI caption. (Cross-source note: the hourly log already calls 06-29→07-05 = W27 — they agree once SSOT is relabeled.)
  3. **MTD/YTD MUST be filled, not left empty — and HARDCODED from the BI image, NOT carried/computed.** Parser v2 only covered Full Week → a bare `### MTD / YTD` placeholder with "null" is WRONG. The BI screenshot already shows the MTD and YTD rows, so OCR them directly.
     - **`parse_mtd_ytd(ocr)` does this** (shipped 2026-07-13): locate the `MTD REVENUE` / `YTD REVENUE` label line, grab the value row immediately ABOVE it, then:
       - MTD rev = first number on that row; MTD **Y/Y% = first pct token on that row**; MTD **M/M% = LAST pct token on that row** (the "MTD REVENUE M/M" column is the rightmost).
       - YTD rev = first number; YTD **Y/Y% = first pct**; YTD **avg = last number** on the YTD value row.
       - Use a STRICT pct regex `[-+]?\d[\d.,]*%` (must end in `%`) — the loose `PCT` pattern mis-classifies the rev number as a pct (comma → float() fails → None).
     - **WARREN CORRECTION (2026-07-13) — DO NOT CARRY Y/Y% from prior week.** First manual fill wrongly wrote SYS MTD Y/Y **+5%** (carried from W27 JSON) when the image actually shows **+3%**; and MTD M/M **+138%** (self-computed) when the image shows **−0%**. Both were wrong. The image is the SSOT for these fields — OCR them, never derive. Verify against the screenshot pixels, not against prior-week JSON.
     - **YTD**: the BI image DOES carry YTD (rev + Y/Y% + avg), so parse it from OCR too — do NOT leave YTD null. (Only leave null if the screenshot genuinely lacks the YTD row, e.g. a partial export. Never fabricate YTD from the 6-week rolling log.)
     - Write MTD + YTD to BOTH the markdown tables AND the JSON `mtd`/`ytd` blocks in `build_payload`/`build_block`.
  4. **Remove obsolete notes** like "_MTD/YTD fields được điền bởi `/ops-weekly-report`... Parser v2 chỉ cover Full Week_" — they are wrong once MTD is filled from BI.
  - This is a Warren-explicit "ghi nhớ" preference (also in WARREN_MEMORY.md). Apply it on every revenue ingest; do not wait for a reminder.

## Revenue Dashboard Regeneration (2026-07-13 — NEW)

The revenue dashboard (`30_KNOWLEDGE_BASE/wiki/dashboards/01_SSOT_01_Weekly_Revenue_Dashboard.html`) was originally a **hand-built static HTML** with `Chart.js` inlined and a single `const PAYLOAD={...};` data line — there was NO generator, so adding weeks to the Revenue Log SSOT did NOT update the dashboard. This caused the dashboard to show `weeks: [W23,W24,W25,W26,W29]` — missing W27/W28 and mislabeling the W27 data block as "W29".

**Fix shipped:** `gen_revenue_dashboard.py` (in `parsers/`) regenerates ONLY the `const PAYLOAD={...};` line from the Revenue Log SSOT — minimal, idempotent, no restructure of the inlined Chart.js / DOM / JS.
- Reads each `## Wxx |` block's `<!-- HERMES REVENUE JSON ... -->` (schema v2: `week/start/end/stores{ALL,LU3,LU5,LU7}{net_rev,rev_ww,covers,covers_ww,avg,avg_ww,tickets,party,target_achv}`, MTD, YTD, delta).
- Maps JSON `ALL` → dashboard `System` key.
- **Derives the correct ISO week label from each block's START date** (`datetime.isocalendar()` → `YYYY-Www`). This auto-fixes mislabeled blocks (the "2026-W29" block spanning 06-29→07-05 is actually ISO **2026-W27**).
- Sorts weeks OLDEST→NEWEST (Chart.js left→right).
- Replaces ONLY the `const PAYLOAD=.*?;\s*(?=</script>)` line via regex — the PAYLOAD line is `...};</script>` with NO trailing newline, so the regex must anchor on the lookahead `(?=</script>)`, NOT `\s*\n`.
- **Verify gate** (in the script): weeks sorted; W28 present; no stale W29; per-store series length == weeks; System latest net_rev > 0; Chart.js still inlined (no `cdn.jsdelivr.net/npm/chart.js`); `new Chart(` present; 7 canvases (`cNet,cCov,cAvg,cParty,cTgt,cRev,cStoreCov`) present; script tags balanced.
- **Run after every new Revenue Log week:** `python3 vault/10_OPERATION_DATA/parsers/gen_revenue_dashboard.py`. When the Monday cron pipeline is eventually built, append this step.

**Ad-hoc verify (2026-07-13, PASS):** generator runs clean + idempotent (2 runs byte-identical on temp copy); output weeks = [W23..W28]; W28 System net_rev 643,954,164 / covers 2,380 / LU3 covers 876 (hand-corrected, verify-gated) match SSOT; W29 stale label removed; Chart.js inlined; all 7 canvases present; script tags 3/3 balanced.

**Generalizable lesson:** any Warren `file://` dashboard whose data lives in a `const PAYLOAD=` / `const D=` line MUST have a generator that rebuilds that line from the SSOT — never hand-author the data array. A static dashboard silently drifts the moment a new week/block is added (the verify gate only checks the JSON parses, not that it's complete).

**P3 — OCR column-shift recovery (Power BI).** A store screenshot can OCR with a shifted column layout: LU3 covers read as `266,211` (actually `876`), tickets misread. The verify_gate party-size check will FAIL (exit 2) — that's the intended signal.
- **Recovery:** derive the missing store's covers from `SYS.covers − (other two stores' covers)`. Cross-check: LU5 722 + LU7 782 = 1,504 → LU3 = 2,380 − 1,504 = 876. Verify net_rev: 233,201,164 + 198,461,000 + 212,292,000 = 643,954,164 = SYS ✓. avg = net÷covers. Feed corrected JSON via `--test-json`.
- **W/W% OCR is STRUCTURALLY UNRELIABLE on this BI layout — treat as a manual-confirmation field, NOT an auto-parsed one.** The W/W% numbers sit on colored bar charts; liteparse frequently DROPS them, leaving a lone bare digit (e.g. the value row renders as `9 REVENUE W/W  % COVERS W/W  % SPEND/COVER W/W` with the real `+15.9% / −3.2% / +9.5%` gone). A naive `_block_pct` using a loose `PCT = r"[-+]?[0-9][0-9.,]*%?"` then matches the surviving bare `9` (the `%?` optional makes the number match as a pct) → assigns **+9% to ALL THREE stores**. This is exactly what happened 2026-07-13 (Warren caught "cả 3 đều 9% sai bét"). The real W/W% came from **WARREN READING THE IMAGE** (LU3 +17%, LU5 −3%, LU7 +11%), not from OCR and not from derivation.
  - **CORRECTION to old advice "derive W/W from prior week's log":** Do NOT auto-derive W/W% from the prior SSOT week. That is a DIFFERENT computation (covers-WoW) and can also be wrong; more importantly it silently overrides the BI image value Warren can see. Correct flow: parser reads W/W% from OCR when reliable; when OCR is unreliable, returns `None`; flags `⚪ — (OCR unreliable, verify)`; then **WARREN confirms the true value from the image** and it gets filled manually into the block + JSON. Trust the image/Warren, never fabricate or derive-and-assume.
- **P6 — W/W OCR: 3-column rule + liteparse-mandatory (final fix, 2026-07-13).** The +9%-all-stores bug went through two fixes; the FINAL one is the robust one — record it precisely:
  - **liteparse is MANDATORY (Warren: "it's a must").** OCR MUST go through `liteparse` (npm CLI primary, `LiteParse` class fallback) — never a raw `pytesseract`/other wrapper, and never bypass. When Warren sends a screenshot, run `liteparse parse <img>` FIRST (HARD GATE); only fall back to vision if liteparse returns empty. liteparse reads the W/W row cleanly on GOOD-quality images (09-19 batch: `7% 7% -0%` etc. parsed perfectly). The earlier "07-30 dropped W/W" was IMAGE-QUALITY (murky bar-chart render), NOT a liteparse failure — liteparse was fine, the OCR just lost digits on a bad render. Do NOT blame or swap liteparse.
  - **The garble signature:** on a bad render the W/W value row collapses to a lone bare digit, e.g. `9 REVENUE W/W  % COVERS W/W  % SPEND/COVER W/W` (real `+15.9% / −3.2% / +9.5%` gone). A naive `_block_pct` with loose `PCT = r"[-+]?[0-9][0-9.,]*%?"` matches the surviving bare `9` (the `%?` optional makes the number match as a pct) → assigns **+9% to ALL THREE stores**. This is exactly what happened 2026-07-13 (Warren caught "cả 3 đều 9% sai bét").
  - **Final fix shipped:** `parse_ww(ocr)` finds the single label line holding `REVENUE W/W` + `COVERS W/W` + `SPEND/COVER W/W` together, takes the value row ABOVE it, extracts ALL strict-pct tokens `[-+]?\d[\d.,]*%`, and **requires ≥3 pcts** — if fewer, returns `{}` (all W/W = None, never a guessed single digit). This means: clean image (3 pcts) → all 3 cols parsed; garbled image (1 pct) → None, flagged for Warren. The single-digit-rejection guard from the intermediate fix was DROPPED because it wrongly rejected legit single-digit values like `7%`; the 3-column-count rule is the real discriminator (a valid W/W row always has 3 columns).
  - **Full W/W pipeline (shipped):** `parse_one_bi` calls `parse_ww` → `d["rev_ww"/"covers_ww"/"avg_ww"]` (avg_ww = SPEND/COVER W/W). `build_block` flags `⚪ — (OCR unreliable, verify)` when any is None (never `🟡 +0%`). Verify gate still passes (it only checks sum/avg/party, not W/W%).
  - **WARREN-PROVIDED W/W (W28 actual):** SYS +7%/+7%/−0% · LU3 +17%/+16%/+1% · LU5 −6%/−3%/−3% · LU7 +11%/+10%/+1%. These came from Warren reading the image (after OCR dropped them on the 07-30 render); once the 09-19 clean render was OCR'd, liteparse returned the SAME numbers — confirming liteparse + the 3-column rule is the durable path.
  - **Lesson for next ingest:** run the parser on the BEST-quality screenshot available; if W/W comes back None, ask Warren for the numbers (do not invent). The 3-column rule guarantees no +9%-style fabrication even on a bad render.

**P4 — Always re-verify independently.** After the parser writes, run an ad-hoc `hermes-verify-*.py` in `%TEMP%` that re-reads the output log + recomputes sums/R/1k from scratch (different method than the parser). Parser's own verify_gate is necessary but NOT sufficient — it runs the same code path. Independent recompute is the MANDATORY VERIFY GATE (Warren rule). Sample:
  ```python
  # recompute: sum 3 stores == SYS; avg=net//covers; R/1k = reviews/covers*1000
  # assert against the written markdown block, not the in-memory dict
  ```

## Log Helpers in `_utils.py`
- `fetch_gviz(sheet_id, gid)` → gviz JSON table
- `build_col_map(cols)` → label→index
- `gviz_cell(row, idx)` → safe cell value
- `week_bounds(offset)` / `prev_week_bounds(start)` / `make_week_id(start)`
- `insert_or_replace_weekly(path, week_id, block)` → newest-on-top with dedup
- `prepend_block(path, block, week_id)` → preserves YAML frontmatter + updates `last_updated`

## Patching Python Files: Line-Index Fallback
When exact string replace fails because of quoting/escape differences (notably `\n` inside prompt strings), patch by **line index**:

```python
from pathlib import Path
p = Path(r'<path>.py')
lines = p.read_text(encoding='utf-8').splitlines()
lines[<0-based-index>] = '<replacement line>'
p.write_text('\n'.join(lines), encoding='utf-8')
```

Use `grep -n` or `sed -n '<start>,<end>p'` to find the target line first.

**Reliability note:** For large multi-line replacements (>20 lines), `patch` can corrupt indentation on Windows (known issue with fuzzy matching). Prefer writing a temp `.py` script via `write_file` and executing it via `terminal + python3 <script>`. This avoids the fuzzy matching entirely. Single-line or small-block changes (≤5 lines) are safe with `patch`.

## Revenue Query Route
When Warren asks for revenue by date or week:
1. First check `vault/10_OPERATION_DATA/01_Weekly_Revenue_Log.md` for weekly summaries.
2. If a specific date is needed, query GSheet `LU_COL_ENGINE_V4`:
   - `Revenue` (gid 762945748)
   - `07_COL_Weekly_Log` (gid 1732633441)
3. Cite the source path and line range in the answer.

## Inbox CSV Rule
`.csv` files in `_inbox/` are **NOT auto-mapped** to GrabFood ([4]). Only map them when Warren explicitly confirms they are raw GrabFood data AND the week is explicitly defined.

## Pre-Redesign Verification Rule (CRITICAL, learned 2026-07-08)

Before proposing to **drop / replace / redesign** any pipeline component (GSheet tab, parser,
SSOT file), **READ THE ACTUAL CODE** that consumes it. Do NOT assume a component is unused
based on a prior conversation summary.

**Incident:** A prior summary stated "CPH dropped GSheet, moved to vault-only." Acting on that,
Hermes proposed OPS-COL should stop reading CPH. Warren corrected: *"no, bạn ko hiểu ý tôi"*
— `ops_col.py` STILL reads `02_MASTER_CPH` every `/ops-col` run to compute `wage = hours × CPH`.
The GSheet was the live sync TARGET, not dead weight.

**Rule:** When a user mentions a component (e.g. "bring back the old table", "the GSheet is
still live"), grep the codebase for that component's identifiers (tab name, gid, variable) and
CONFIRM the consumer before changing anything. A compaction summary is NOT ground truth — the
code is. If the summary and the code disagree, the code wins and the summary was stale.
Before running `/process-logs` or any parser, HORION must read `vault/00_CORE_LOGIC/ops_parsers_guide_for_HORION.md`. That file is the operational reference for parser mapping [1..10], input/output paths, and non-IT flow. It is not a wiki insight and should not be moved into `vault/30_KNOWLEDGE_BASE/wiki/`.

## `/ops-process-logs` Canonical Workflow
Primary reference: `.kilo/command/ops-process-logs.md`

When Warren types `/ops-process-logs`:
1. `list_files(path="vault/_inbox/")`
2. Auto-detect file types:
   - `*.csv` → GrabFood
   - `*HR*.xlsx` → HR
   - `*Payroll*LUS*.xlsx` → Payroll CPH
   - `*.png/*.jpg` → Revenue (needs 4 files)
   - if multiple matches, list and ask Warren which to run
   - if none, show parser selection menu [1..10]
3. Run parser:
   - 1 parser: normal run, preview output, confirm before write
   - ≥2 parsers: **parallel** via multiple `execute_command()` calls in one turn
4. After all complete: **Auto-sync OPERATION_INDEX** via `python vault/scripts/ops_index_watchdog.py` — updates `last_updated` dates, adds new files, flags stale frontmatter. Do not block the workflow on this step. Do not notify unless gap >30 days or new files appear.
5. **Wiki Insight Check** — surface 🔴 flags / trend breaks for Warren to choose `/ops-ingest` candidates. **Never auto-write wiki.**
6. Cleanup: ask if Warren wants to delete processed files from `_inbox/`.

## OPERATION_INDEX Protocol
Single source of truth: `vault/10_OPERATION_DATA/OPERATION_INDEX.md §Operational Logs`.

- **Canonical sync tool:** `vault/scripts/ops_index_watchdog.py`
  - Reads each log file's YAML frontmatter `last_updated`
  - Writes the date into the table
  - Auto-adds new log files not yet in the table
  - Flags files with missing or >30-day-stale frontmatter
  - Idempotent: safe to run after every `/process-logs` or `/ops-ingest` that writes logs
- **Command sync rule:** any command file referencing `10_OPERATION_DATA/` logs must reference `OPERATION_INDEX.md §Operational Logs` as the source of truth, not a hardcoded list. If a command lists N sources but the index has M rows, flag the mismatch.
- **New file detection:** the watchdog excludes `OPERATION_INDEX.md`, `pulse_log.md`, `weekly_connections_log.md`, and `morning_briefs/` automatically.
- Manual trigger: `.kilo/command/ops-index-sync.md` runs the same watchdog script.

## Update Triggers
Run the watchdog automatically after:
- any successful parser run from `/ops-process-logs`
- any `/ops-ingest` that modifies a log file
- `/ops-index-sync` manual command

Do NOT require Warren confirmation for these index updates; they are metadata-only.

## Parser Registry (from `.kilo/command/ops-process-logs.md`)
| # | Input | Script | Output | Frequency | Cron-ready |
|---|-------|--------|--------|-----------|------------|
| 1 | GSheet "Hourly_Revenue" (GID 1841157748) | `hourly_cover_parser.py` | `09_Hourly_Cover_Revenue_Log.md` | Weekly (Mon) | ✅ v4.1 |
| 2 | GSheet PRICE_CHANGE (GID 865155568) | `cogs_parser.py` | `03_COGS_Supplier_Monthly_Log.md` | Monthly | ✅ v3.4 |
| 3 | GSheet "LTO Log" | LTO parser | `04_LTO_Weekly_Log.md` | Weekly (Mon) | ✅ v2.0 |
| 4 | GSheet "Google Review Log" | Google Reviews parser | `05_Google_Review_Weekly_Log.md` | Weekly (Mon) | ⏳ |
| 5 | GSheet "Grabfood" / `*.csv` | GrabFood parser | `06_GrabFood_Weekly_Log.md` | Weekly (Mon) | ✅ |
| 6 | Screenshot Power BI (4 images) | Manual ORION step | `01_Weekly_Revenue_Log.md` | Weekly (Mon) | Manual |
| 7 | `*HR*.xlsx` | HR parser | `02_HR_Weekly_Log.md` | Weekly | ⏳ |
| 8 | GSheet COL_Weekly | COL parser | `07_COL_Weekly_Log.md` | Weekly (Mon) | ✅ v4.0 |
| 9 | GSheet "11_Item_Sales" | Item Sales parser | `11_Item_Sales_Weekly_Log.md` | Weekly (Mon) | ⏳ |
| 10 | `*Payroll*LUS*.xlsx` | Payroll CPH parser (`payroll_cph_robust.py`) | `12_Wage_Structure_by_Role_Monthly.md` + `cph_result_YYYYMM.csv` | Monthly | ⏳ (robust variant added 2026-07-08; full redesign in progress — see Payroll CPH subsection) |
| 11 | Star Horse GSheet + Recipe_Index.json | `menu_gp_parser.py` (`vault/scripts/`) | `14_Menu_GP_Monthly_Tracker.md` | Monthly (manual, ngày 5) | ⏳ |
| 12 | GSheet `10_Wastage_WriteOff_Monthly_Log` (Data tab, gid 2147354564) + Revenue from xlsx Sheet1 | `wastage_parse_gen.py` (`vault/scripts/`) | `10_Wastage_WriteOff_Monthly_Log.md` (markdown entry, 11 sections, HERMES template) + `COGS_Dashboard_{month}.html` + `Wastage_Dashboard_{month}.html` | Monthly (ngày 5, CFO report arrives) | Manual (`/cogs-ingest`, `/cogs-report`, `/cogs-gen`) |

GSheet ID for all GSheet-driven parsers: `1ZtIocc_Ic1z-tO1JGd4ZLnRB_7ZHHkvpJ5emaWJyeEE`

**Cron-ready = `✅` means parser is verified to run end-to-end (fetch → parse → format → write) in headless mode as part of Monday 09:45 pipeline.**

## OS Layer Guard
- This skill governs `.kilo/skills` parser execution only.
- HORION lives in Hermes/Windows; ORION owns `.kilo/`. Do not write ORION artifacts from HORION sessions.
- Use `read_file` + `terminal` for vault/script edits; avoid `patch`/`write_file` path pitfalls on Windows.

## GSheet Parser Debugging Patterns (updated 2026-06-30)

### Incomplete Parser `run()` Function
**Symptom:** Parser runs (fetches data, parses rows) but exits without writing to log file.

**Root cause:** `run()` function was written but the developer never completed it — missing `entry = build_entry(...)` and `LOG_FILE.write_text(...)` calls at the end.

**Fix:** Add the last ~20 lines to `run()`:
```python
entry = build_entry(week_start, week_end, filtered, prev_parsed)

if LOG_FILE.exists():
    existing = LOG_FILE.read_text(encoding="utf-8")
    pattern = rf"(## {re.escape(week_id)}.*?)(?=\n## |\Z)"
    replaced = re.sub(pattern, "", existing, flags=re.DOTALL).strip()
    if week_id in existing:
        new_content = entry + "\n\n---\n\n" + replaced if replaced else entry + "\n"
    else:
        new_content = entry + "\n\n---\n\n" + existing if existing else entry + "\n"
else:
    new_content = entry + "\n"
LOG_FILE.write_text(new_content, encoding="utf-8")
```

**Verification:`python3 <parser>.py` should print `✅ Written → <log_path>`.

### GSheet `Date()` vs `DateTime()` Regex Mismatch
**Symptom:** All parsed dates return `None`, resulting in 0 rows filtered for the current week.

**Root cause:** GSheet gviz API returns `Date(2026,5,14,22,31,0)` (without "Time" in the function name), but the parser regex expects `DateTime(...)`.

**Fix:** Use `Date(Time)?` pattern:
```python
m = re.match(r"Date(Time)?\((\d+),(\d+),(\d+),(\d+),(\d+),(\d+)\)", s)
# Groups: (Time_or_None, year, month, day, hour, min, sec)
year = int(m.group(2))
month = int(m.group(3)) + 1  # 0-indexed in GSheet
```

### Store Name Mapping Differs Per GSheet Tab
**Symptom:** Parser returns 0 rows because store names in the GSheet tab don't match the parser's STORE_MAP.

**Root cause:** Each GSheet tab uses different store name conventions:
| Tab | Format | Example |
|-----|--------|---------|
| COL_Weekly | `LU3-LTT-Q1` | `LU3`, `LU5`, `LU7` |
| Grabfood | `"L'Usine Lê Thánh Tôn"` | Full store name |
| Hourly_Revenue | `LU3-LTT-Q1` / `LU3-LTT-Q1 Total` | With Total variants |
| Google_Review | `"L'Usine Lê Thánh Tôn"` | Full store name |

**Fix:** Run a quick diagnostic to discover store names:
```python
stores_found = set()
for row in rows:
    cells = row.get('c', [])
    if cells and cells[0]:
        v = cells[0].get('v')
        if v:
            stores_found.add(v)
print('Stores in GSheet:', sorted(stores_found))
```

### Grand Total vs Store Total Row Distinction
**Symptom:** No daily totals found, or impossible numbers.

**Root cause:** In the Hourly_Revenue pivot table:
- "Grand Total" row is **system-wide** (ALL stores combined)
- "LU3-LTT-Q1 Total" etc. rows are **per-store daily totals**
- The parser was looking for "Grand Total" when it should use "LU3-LTT-Q1 Total"

**Fix:** Filter out "Grand Total" rows (system-level) and use store-specific Total rows ("LU3-LTT-Q1 Total") for daily totals:
```python
is_store_total = store_raw in {"LU3-LTT-Q1 Total", "LU5-CM-Q7 Total", "LU7-SC-Q1 Total"}
is_grand_total = store_raw == "Grand Total"
if is_store_total: store_rows[current_store_raw]["grand_total"] = daily_data
if is_grand_total: continue  # skip system-level grand total
```

### Hourly_Revenue Pivot Table Column Mapping (verified 2026-06-15)

**Critical:** Tuesday revenue is at column index 7, NOT 8. Do NOT use the formulaic `3 + i*3` approach — hardcode the mapping.

| Day | Covers Col | Revenue Col | Header Pattern |
|-----|------------|-------------|----------------|
| Mon | 3 | 5 | "Monday Number of guests" / "Gross Sales (after discount), VND" |
| Tue | 6 | 7 | "2. Tuesday Number of guests" / "Gross Sales (after discount), VND" |
| Wed | 8 | 10 | "3. Wednesday Number of guests" / "Gross Sales (after discount), VND" |
| Thu | 11 | 12 | "4. Thursday Number of guests" / "Gross Sales (after discount), VND" |
| Fri | 13 | 14 | "5. Friday Number of guests" / "Gross Sales (after discount), VND" |
| Sat | 15 | 16 | "6. Saturday Number of guests" / "Gross Sales (after discount), VND" |
| Sun | 17 | 18 | "7. Sunday Number of guests" / "Gross Sales (after discount), VND" |
| Grand Total | 19 | 20 | "Grand Total Number of guests" / "Gross Sales (after discount), VND" |

**Python constant:**
```python
DAY_COLS = {
    "mon": {"covers": 3, "revenue": 5},
    "tue": {"covers": 6, "revenue": 7},
    "wed": {"covers": 8, "revenue": 10},
    "thu": {"covers": 11, "revenue": 12},
    "fri": {"covers": 13, "revenue": 14},
    "sat": {"covers": 15, "revenue": 16},
    "sun": {"covers": 17, "revenue": 18},
}
```

### Double `vault/` Path Bug
**Symptom:** `FileNotFoundError` on file that definitely exists.

**Root cause:** Script uses `VAULT_ROOT / "vault" / "10_OPERATION_DATA"` where `VAULT_ROOT` already points to `vault/`.

**Verify:**
```bash
grep -rn 'VAULT_ROOT.*vault.*OPERATION_DATA' vault/scripts/ vault/10_OPERATION_DATA/parsers/
```
If the path constructs like `VAULT_ROOT / "vault" / "10_OPERATION_DATA"` and `VAULT_ROOT = Path(__file__).parent.parent` (which resolves to the vault directory), the `/vault/` segment is duplicated.

**Fix:** Remove the duplicate `vault/` segment:
```python
# BAD:
LOG_FILE = VAULT_ROOT / "vault" / "10_OPERATION_DATA" / "04_LTO_Weekly_Log.md"
# GOOD:
LOG_FILE = VAULT_ROOT / "10_OPERATION_DATA" / "04_LTO_Weekly_Log.md"
```

### `fetch_sheets_api()` Returns Dict, Not Tuple (2026-06-30)
**Symptom:** Calling `cols, rows = fetch_sheets_api(id, gid)` returns `"cols"` and `"rows"` as **strings** (the dict keys), not the actual column/row data. Subsequent `row.get("c", [])` fails with `AttributeError: 'str' object has no attribute 'get'`.

**Root cause:** `fetch_sheets_api()` (in `_utils.py`) returns a single dict `{"cols": cols, "rows": data_rows}`, but tuple unpacking on a dict iterates over its **keys**, not values. Python does not warn — `a, b = {"x": [...], "y": [...]}` assigns `a="x"`, `b="y"`.

**Fix:** Access via dict subscript or use the `fetch_sheet()` wrapper that parsers already define:
```python
# WRONG — get string keys:
cols, rows = fetch_sheets_api(SHEET_ID, GID)

# RIGHT — dict access:
result = fetch_sheets_api(SHEET_ID, GID)
cols, rows = result["cols"], result["rows"]

# OR use the dedicated wrapper most parsers already have:
def fetch_sheet():
    result = fetch_sheets_api(SHEET_ID, SHEET_GID)
    return result["cols"], result["rows"]
```

**Verification:** `type(rows)` should be `<class 'list'>`, not `<class 'str'>`.

### GSheet CSV Export — Alternative When `_utils` Import Fails (2026-07-01)
**Symptom:** `from _utils import fetch_sheets_api` raises `ModuleNotFoundError` because PYTHONPATH doesn't include the parsers directory (e.g., running from `/c/Users/khoans/` instead of `vault/10_OPERATION_DATA/parsers/`).

**Alternative:** Use the Google Sheets CSV export endpoint directly via `urllib.request` — no internal module dependency:
```python
import urllib.request, csv, io
SHEET_ID = "1ZtIocc_Ic1z-tO1JGd4ZLnRB_7ZHHkvpJ5emaWJyeEE"
GID = "1732633441"  # COL_Weekly tab
url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
resp = urllib.request.urlopen(req, timeout=30)
text = resp.read().decode("utf-8-sig")
reader = csv.DictReader(io.StringIO(text))
# Now access columns by name: row["Revenue"], row["Total_Hours_Whole_Store"]
```

**Benefits over gviz API:**
- Works from ANY working directory (no PYTHONPATH setup needed)
- `csv.DictReader` gives named columns — no index guessing via `build_col_map()`
- No `gviz_cell()` / `build_col_map()` dependency

**Limitations:**
- Read-only (can't append to sheet)
- `User-Agent` header required to avoid 403
- UTF-8-BOM encoding -> `encoding="utf-8-sig"`
- Public sheets only (the L'Usine ops GSheet is public-readable, so this works)

**Use case:** Quick diagnostic queries, ad-hoc analysis, one-off data snapshots. NOT for parser production code — parsers should use `fetch_sheets_api()` for consistency with the pipeline.

### GSheet Percentage Values Are Strings With `%` Suffix (2026-06-30)
**Symptom:** Parser processes N rows but every item shows 0% change (`pct=0.0`). All price increases/decreases are invisible.

**Root cause:** The GSheet Sheets API returns percentage-formatted cells as **strings** like `"10%"`, `"-1%"`, `"40%"`, not as decimal numbers. A naive `float(str(val))` raises `ValueError` and falls back to `0.0`.

**Fix:** Strip the `%` character before conversion — and keep in mind the value is already in percent units (10 = 10%, not 0.10):
```python
def to_float(val):
    if val is None: return 0.0
    s = str(val).replace(',', '').replace(' ', '').replace('%', '')
    try: return float(s)
    except: return 0.0
```

**Impact formula reminder:** With percent units (pct=10 means 10%), the correct formula is:
```python
impact = pct / 100 * price_old * volume
```
NOT `pct * price_old * volume`.

**Existing parsers to audit:** `cogs_parser.py` v3.2 has this bug — its `to_float()` in `cogs_parser.py:158` does not strip `%`. It works with the gviz endpoint (which returns raw numbers) but breaks when switched to `fetch_sheets_api()` (which returns formatted strings).

### Payroll CPH — External Excel Template Drift (2026-07-08)

`payroll_cph.py` v2 is **brittle to HR template changes**. June 2026 payroll
(`Monthly Payroll Report (LUS) 06.2026 - OPS.xlsx`) has a letterhead + 2-row header
at row 11 (not `header=1`), and a filename with no month word (`06.2026` not
`June 2026`) → v2 silently mis-parses / can't infer period.

**Fix shipped:** `payroll_cph_robust.py` — same CPH math (Total cost to Company minus
incentives, CPH = cost/hours, segment map, resignee exclusion, Hong Han halving, red
flags) but with:
- **Header auto-detect:** scan rows 1-40 for a row containing both `No.` and `Full Name`;
  read with `header=row-1`; drop the column-number junk row (No. is digit AND Full Name
  is digit).
- **Flexible period:** `June 2026` word OR `06.2026` (`\b(\d{2})\.(\d{4})\b`) OR explicit
  `YYYYMM` 2nd arg.
- Reuses `cph_config.py` (do NOT duplicate SEGMENTS_ORDER/BENCHMARKS/SEGMENT_MAP).

**Use `payroll_cph_robust.py` for monthly `/cph` runs** until the full CPH-system
redesign (input template → pipeline → wiki → dashboard) is signed off by Warren.
CSV output: `vault/10_OPERATION_DATA/monthly/cph_result_YYYYMM.csv`.

**v3 redesign COMPLETE (2026-07-08):** `payroll_cph.py` is now the canonical v3 — it
MERGED the robust loader AND fixed the Full-Time `Working Hours = 0` CPH bug
(`calc_hours()` derives hours from `Payable Days × 8` for Full-Time staff). v3 also
writes CSV + appends `_accumulation/cph.json` + prepends a month block into
`12_Wage_Structure_by_Role_Monthly.md` (idempotent on `### YYYY-MM`). `payroll_cph_robust.py`
is now REDUNDANT — archive/delete it. Dashboard: `gen_cph_dashboard.py` →
`CPH_Dashboard.html` (green theme, LU3/LU5/LU7/System filter).

**⚠️ 02_MASTER_CPH is NOT dropped — it is the SYNC TARGET.** The 2026-07-08 redesign moved the
*human-readable SSOT* out of GSheet, but `02_MASTER_CPH` (gid `871133523` in `LU_COL_ENGINE_V4`)
**remains the live CPH rate source that `/ops-col` (ops_col.py) reads to compute wage = hours × CPH**.
To keep it current, `payroll_cph.py` auto-calls `sync_cph_gsheet.py` at the end of `main()`:
- `vault/10_OPERATION_DATA/parsers/sync_cph_gsheet.py` reads `cph.json`, **FULL-REBUILDS** the
  `02_MASTER_CPH` tab (newest-on-top, idempotent) and is auto-called by `payroll_cph.py` at
  the end of `main()`:
  - Reads header row (row 0), preserves it.
  - Builds all data rows from `cph.json`, **sorted YEARMONTH DESC** (202606 before 202605).
  - Clears `A2:I1000`, writes `header + rows` via `values.update(range A1:I{n})`.
  - **NOT append/upsert** — full rebuild guarantees GSheet never drifts from vault SSOT.
  - `ops_col.py load_cph()` keys by YEARMONTH (dict), so row order does not affect it.
- **Auth:** SA key scope changed `spreadsheets.readonly` → `spreadsheets` (WRITE) in
  `vault/10_OPERATION_DATA/scripts/modules/_utils.py` on 2026-07-08. The OAuth token
  (`google_token.json`) was REVOKED (invalid_grant) — do NOT use it for write; SA key is durable.
- **Vacant (CPH=0) syncs as 0** — correct as actuals; `ops_col.py resolve_cph()` falls back to
  last-known-good month, so a 0 never leaks as a false rate into COL.
- Verify after any edit: temp `hermes-verify-*.py` that re-reads `cph.json` + the GSheet tab and
  cross-checks `(month,store,role)` values match. Confirm `scopes` includes `spreadsheets` (not readonly).

**CRITICAL CPH bug to never reintroduce:** Full-Time staff have blank `Total of Working
Hours` → must derive `Payable Days × 8`. See
`references/payroll-cph-v3-hours-and-large-write.md` §1 for the fix + verification
assertions (LU7 FOH Bar ≈ 49,816; LU3 BOH Cook ≈ 45,969 on June 2026).

**CRITICAL C1 — `col_index()` returning `-1` silently corrupts ALL output (time-bomb).**
**Symptom:** One renamed HR header → every downstream `r[ci_x]` indexes `r[-1]` (the LAST
column, valid Python, NO error). Employee filter runs on last column, store mis-detected,
cost = garbage, hours = 0 → **all CPH = 0**, no crash, confidently wrong.
**Root cause:** `col_index()` returns `-1` on missing column; `-1` is a valid list index.
**FIX (mandatory):** After `detect_header()` + `col_index()` for ALL required columns
(Emp.Code, Location, Position, Employee Status, Total cost to Company, Working Hours/Days,
Working Type), **VALIDATE** — if any required column resolved to `-1`, RAISE with the exact
missing header name. Do NOT fall through. Also unify detection: `detect_header()` uses
substring (`"total cost" in joined`) but `col_index()` uses exact-match — a cost column
labeled `"Total Cost"` (no "to Company") passes detect yet yields `-1`. Make both substring
OR both exact. VN templates: add `"toàn thời gian"` to the Full-Time keyword check in
`calc_hours()` (EN-only `"full"` misses VN payroll). See `references/payroll-cph-v3-hours-and-large-write.md` §2.

**CRITICAL I4 — Atomic JSON write (never corrupt `_accumulation/cph.json`).**
**Symptom:** If the script dies mid-write (crash/Power loss), `cph.json` is left half-written
→ next run JSONDecodeError → whole history lost.
**FIX:** Write to a temp file then `os.replace()` (atomic on Windows/posix):
```python
import tempfile, os
tmp = ACC.with_suffix('.tmp')
json.dump(data, open(tmp,'w',encoding='utf-8'), ensure_ascii=False, indent=1)
os.replace(tmp, ACC)  # atomic, overwrites only on success
```
Same pattern for any accumulation JSON the parser maintains.

**Data-integrity watch:** a segment computing to **0** is often a REAL structural
vacancy, not a bug — June 2026 had 9 resignees, 6 in LU3 FOH, so FOH Management /
FOH Floor Lead / FOH Bar Team all = 0 (every person in those segments was a resignee,
correctly excluded). NEVER "fix" a zero by re-including resignees — flag it for Warren.

**Doc-rot WARNING:** vault files (`12_Wage_Structure_by_Role_Monthly.md`,
`CPH_Phan_Tich_Rolling.md`) reference skill names `ops-cph-payroll`,
`payroll-cph-engine`, `/ops-cph-payroll` that **do NOT exist** as skill files.
Canonical pipeline = `payroll_cph.py` + `cph_config.py` (command `/cph`). Do NOT create
phantom skills to satisfy those references — fix the references instead.

**Generalizable rule:** any parser reading HR/Finance Excel must auto-detect the header
row and parse the period flexibly. Never hardcode header-row index or a single
filename format for externally-produced spreadsheets — they drift without notice.

See `references/payroll-cph-xlsx-variance.md` for the loader code + ad-hoc verify script.

### Parser End-to-End Verification Checklist
After any parser fix, run this checklist:

```python
def verification_checklist():
    checks = [
        ("Completeness", "run() ends with build_entry() + write_text()"),
        ("Store names", "STORE_MAP keys match GSheet tab (not another tab)"),
        ("Column mapping", "Day columns match GSheet header labels"),
        ("Date parsing", "Date(2026,5,14,22,31,0) format handled"),
        ("Grand Total filter", "System-wide Grand Total rows filtered out"),
        ("Store Total handling", "LU3-LTT-Q1 Total rows used for daily totals"),
        ("Revenue conversion", "Gross * 0.882 = Net if applicable"),
        ("Format compliance", "Output matches HERMES TEMPLATE sections"),
        - **Data sanity**, covers < 5000/day, rev/cover 10k-500k, COL% 5-30%
                - **Cross-check**: Compare covers+revenue with `01_Weekly_Revenue_Log.md` for same week. Flag 🔴 if diff >5%. Both sources must match — GSheet hourly counts split orders as covers, Revenue Log (PowerBI) may use different definition.
            ]
    for name, desc in checks:
        print(f"  [ ] {name}: {desc}")
```
- XLSX engine missing: `Import openpyxl failed` → add `--with openpyxl` to `uv run`.
- Headless hang: parser uses raw `input()` → replace with `_ask()` and import from `_utils`.
### Item Sales (Star Horse) Parser v2.0 — Compact 4-Section Format (2026-07-06)

**Version:** v2.0 (was v1.4)
**Format change:** 60% machine (JSON hidden) / 40% human (Exec Summary + Scorecard + Flags). **~38% token reduction per week** (87 lines vs 141 lines).

**New entry structure (4 sections):**
1. **`### 🎯 Executive Summary`** — 4 bullets: System (qty + rev + Δ), Top group, 🔴 Flag (count of price issues), ✅ Star item with CM%
2. **`### 📊 Scorecard`** — 1 compact table (LU3/LU5/LU7/System) with ΔQty, ΔRev, ΔPrice columns. Uses `_pct_change()` helper.
3. **`<!-- HERMES JSON BLOCK\n\`\`\`json\n...\n\`\`\`\n-->`** — Hidden JSON block for Hermes grep. Contains: system, per-store groups (top 80%), top 5 food/drink, BCG quadrants, flags
4. **`### 🔴🔵 Flags & Actions`** — Structured bullets: price alerts, Cost=0 items, Star items, BCG summary, trend warning

**Key changes from v1.4:**
- Removed 40-line HTML template comment from file body (80% token reduction in boilerplate)
- Replaced 3× verbose store group tables (60+ lines) with hidden JSON block (~40 lines)
- Replaced verbose `### Tổng Quan` with compact Executive Summary (includes FBM-style 💡 RECOMMEND)
- Replaced `### So sánh Tuần` with Scorecard (same data, fewer rows)
- Replaced `### Cảnh Báo & Dấu Hiệu` with Flags & Actions (structured, decision-ready)
- Revenue displayed in **M** (triệu VND) in Scorecard, raw VND in JSON

**Hidden JSON block pattern:**
```markdown
<!-- HERMES JSON BLOCK
```json
{
  "week": "W27", "date": "2026-06-29--2026-07-05",
  "system": {"qty": 4280, "rev": 580.5, "rev_vnd": 580450194, "avg_price": 135619},
  "stores": {
    "LU3": {"qty": 1431, "rev": 192.4, "avg_price": 134477, "groups": [
      {"name":"Coffee","qty":383,"pct":26.8},
      ...
    ]}
  },
  "top_food": [{"name":"The Big Breakfast","qty":75}],
  "top_drink": [{"name":"Acqua Panna - 500ml","qty":106}],
  "bcg": {"food":{"total":74,"star":21,"ph":16,"dog":21,"qm":16},"drink":{...}},
  "flags": [{"type":"price","severity":"red","items":["Extra Butter 0đ","Extra Egg 17.6k"]}]
}
```
-->
```

**Key functions changed in v2.0:**
- `build_entry()` — completely rewritten to output 4-section compact format (was building 3 verbose store tables + Top 10 lists)
- `parse_prev_store_summary()` — rewritten to handle BOTH old format (Store Summary) and new format (Scorecard) via line-scan based store-ID matching. Uses `.removesuffix('M')` for "192.4M" format revenue parsing.
- `run()` — removed HTML template extraction, added auto-update of `_accumulation/item_sales.json`

**New module-level helpers (extracted for DRY):**
- `STORES_ORDER = ["LU3", "LU5", "LU7"]` — single constant, used by `build_entry()` and `run()`
- `_pct_change(new, old)` — replaces 10 repeated formulas across `build_entry()`. Returns 0 if old is 0/falsy.
- `_qcounts(items)` — BCG quadrant counter, moved from inner function to module-level (testability)
- `CATEGORY_KEYWORDS` dict — replaces 8-branch `elif` chain in `infer_category()` (dict-driven)

**Parser outputs:**
- Main tracker: `10_OPERATION_DATA/11_Item_Sales_Weekly_Log_Star_Horse_Tracker.md`
- Accumulation JSON: `_accumulation/item_sales.json` (updated automatically after each run)
- Dashboard: `wiki/dashboards/item_sales_trend.html` (Chart.js, green theme, rebuildable via `build_item_sales_dashboard_data.py`)

**Backward compatibility:** Old format entries (W18-W26) in the tracker file are NOT modified. `parse_prev_store_summary()` scans for store IDs in `|`-delimited rows and works with both old and new table headers.

**Cross-check:** `cross_check_revenue()` still active — compares Star Horse net revenue vs `01_Weekly_Revenue_Log.md`. Blocks write if diff >4%.

**Semicolons (avoidance):** v2.0 code review flagged and removed all statement-separator semicolons (e.g., `system_items = 0; system_rev = 0` → separate lines). String-literals with `"; "` are fine.

**Reference:** See `ops-dashboard/references/item-sales-dashboard-session-2026-07-06.md` for full session detail: data extraction, W27 computation, interview outcomes.

---

### COL Weekly Parser v4.0 — Compact Format (2026-07-06)

**Version:** v4.0 (was v3.1)
**Format change:** 5 sections replacing old 6-section format. **53% token reduction** (34 lines vs 73 lines per week).

**New entry structure:**
1. **📋 Executive Summary** — 3 bullets: System, Top concern, Key Takeaway
2. **📋 Scorecard** — 4-row table (LU3/LU5/LU7/Sys) with Rev(M), Hrs, COL%, SPLH(k), Δ Rev%, Δ COL, Pass
3. **📅 Daily COL%** — Single heatmap table (7 days × 4 stores), COL% only — replaces 3 separate daily detail tables
4. **⚡ Key Flags** — Max 3 analytical bullets (not data re-statement)
5. **`<!-- col_data: {...} -->`** — Machine-readable JSON block with all weekly aggregates for fast Hermes grep

**Key removals vs v3.1:**
- `build_flags()` function deleted (replaced by `build_key_flags()` + heatmap)
- Per-store daily detail tables replaced by single heatmap
- Executive Summary restructured to 3 concise bullets

**Key additions:**
- `build_key_flags()` — generates max 3 analytical insights
- `build_json_block()` — compact JSON with weekly aggregates per store + daily COL% data
- JSON block embed as HTML comment for zero-visual-footprint parsing

**Data integrity:**
- `store_agg()`, `fetch_sheet()`, `filter_week()`, `parse_row()` unchanged
- `cross_check_revenue()` ±5% gate still active: blocks (sys.exit 1, no write) when COL revenue vs `01_SSOT_01_Weekly_Revenue_Log.md` differs by **>=5.0%** — at exactly 5.0% it ALERTS (use `>=`, NOT `>`; Warren-set threshold 2026-07-13).
- `build_monthly_summary()` unchanged

**Dashboard companion:** `vault/10_OPERATION_DATA/scripts/gen_col_trend_dashboard.py` generates `COL_Trend_Dashboard.html` (Chart.js, full history W09→W28 = ~20 weeks, green theme). Fetches GSheet directly (not vault markdown) for historical aggregation — do NOT build it from the log's `col_data` JSON blocks (they exist only for recent weeks → sparse dashboard Warren rejected 2026-07-13).

**⚠️ COL PARSER HAS NO CRON — automation gap (found 2026-07-13):** `col_weekly_parser.py` is NOT wired to any cron. The Monday 09:45 orchestrator `run_monday_gsheet_parsers.py` referenced in `CONTEXT.md` **no longer exists** (stale path), so W28 was never auto-parsed even though W28 revenue/GrabFood were ingested. The cron list (`cronjob list`) confirms no job calls `col_weekly_parser.py` — only `gen-today-daily` (10:00), `menu-gp-accumulate` (09:45), `fill-promo-tracking` (14:00) exist. FIX (apply on Warren approval): add a cron `0 45 9 * * 1` that runs `col_weekly_parser.py` + the verify gate (`scripts/verify_col_weekly.py`), mirroring `menu-gp-accumulate`. Until then, COL new weeks must be run MANUALLY after each Monday. Also: `COL_Trend_Dashboard.html` was stale (only to ~W09) — `gen_col_dashboard.py` reads GSheet directly, so it won't reflect log edits; rebuild it when needed.

**Reusable verify script:** `scripts/verify_col_weekly.py` (under this skill) does the independent recompute + week-selecting JSON parse for any COL week. Run `python verify_col_weekly.py` (current week) or `--week 2026-W28`. It already encodes the two ad-hoc pitfalls (dict-unpack, multi-block JSON select) — copy it rather than hand-rolling a temp verify. See `verify-parser-output` skill pitfalls for the full write-up.

**Retroactive source amendment → stale log (2026-07-13):** A prior-week COL log entry can go stale if the GSheet wages are edited after logging. W28 parser's `D COL` vs the *written* W27 log looked inconsistent, but independent W27 recompute from the live sheet showed W27 itself had been amended upward (LU3 21.7→23.3%, SYS 13/21→11/21). The parser reads current source; the log is a frozen snapshot. When a delta looks wrong vs the written prior entry, recompute the prior week from the live source before blaming the parser — and decide with Warren whether to refresh or annotate the stale entry (never silently "fix" history).

### Hourly Cover Parser v5.0 — Hybrid Format (2026-07-06)

**Version:** v5.0 (was v4.5)
**Format change:** 60% machine (compact JSON) + 40% human (Decision Board + Exec Summary). **~55% token reduction vs v4.5** (from 18-line pretty JSON to 1-line compact JSON, ALL table dropped, Conversion block moved to frontmatter).

**New entry structure (6 sections per week):**
1. **`### 📊 Data`** — 1-line compact JSON block. Schema: `{week_id, period, rev, covers, stores: [{id, c, r, rc}], vs: {covers_pct, revenue_pct}}`. ~315 chars vs 3208 chars in v4.5.
2. **`### Executive Summary`** — 3 bullets: System (covers + rev), Top/Bottom, Key Takeaway
3. **`### 🔥 Decision Board`** — Table with Flag(🟢🟡🔴), Store, Detail, 🧑‍🍳 FBM Recommend
4. **`### Hourly Detail — <Store>`** — 3 store tables. Day headers = 1-letter (M T W T F S S). Revenue in **M** (triệu VND), 1 decimal. Format: `covers·revenue_M` (e.g. `10·2.8M`). **No ALL table** (derivable).
5. **`### MTD`** — Monthly summary table (covers + gross rev + net payout per store)
6. **`### 📈 Dashboard`** — Link to `dashboard.html`

**Key changes from v4.5:**
- Revenue unit changed from `k` (thousands) to `M` (millions) — `round(val/1e6, 1)`
- JSON block dropped hourly arrays (stays in markdown tables for human reading)
- Decision Board replaces Weekly Roll-up table
- ALL hourly table removed (Hermes derives from 3 stores)
- Cross-check section only written when diff >2% (silent when matching)
- Conversion section moved from weekly body to frontmatter (written once)
- ASCII art template comment (30 lines) replaced by 1-line compact comment

**Dashboard companion:** `30_KNOWLEDGE_BASE/wiki/09_hourly_cover_revenue/dashboard.html` — Chart.js, green theme, 5 charts (system trend, store covers, rev/cover, store revenue, mix). Hardcoded data array, regenerated after each weekly parse.

**Cross-check gate (HARD):** After writing W27 entry, compare covers+revenue against `01_Weekly_Revenue_Log.md` for the same week. If diff >5%, show 🔴 flag on dashboard. This catches counting-method differences (split orders vs actual covers).

### Week detection in `col_weekly_parser.py`
- The parser can infer week from `--week YYYY-Www`, otherwise compute `prev_week_bounds()`.
- Do NOT roll your own ISO week math. Reuse `week_bounds()` / `prev_week_bounds()` from `_utils`.
- If you patch this file, keep the helper imports intact; otherwise the week filter returns nothing.
- Weekly delta section requires two week ranges: current + previous. Ensure both filters run.

### Week key mismatch: use `make_week_id()` so all logs share the same `YYYY-Www` format.
- Duplicate config drift: never copy `CPH_BENCHMARKS`/`SEGMENT_MAP` into parser files.
- Frontmatter edits: do not edit YAML frontmatter with hand-rolled string ops unless parsing it properly; use `insert_or_replace_weekly()` instead.
- `patch`/`write_file` path quirk on Windows: `/c/Users/...` can become `C:\\c\\...`. Use `C:/Users/...` or `terminal` + Python heredoc for batch edits.
- Post-parse Excel cleanup often fails on Windows because the file is still open. Wrap `os.remove()` cleanup in try/except or skip on `PermissionError` instead of failing the whole parse.

### COGS Parser — Workflow & Patterns (v3.4)

**Data flow:** Supply Chain (Thao) fills FM-PUR-06 Excel form → data entered into GSheet tab → `cogs_parser.py` reads GSheet → writes `03_COGS_Supplier_Monthly_Log.md`.

**Tab name discrepancy:** The frontmatter says `sheet_name: PRICE_CHANGE` but the actual GSheet tab for GID `865155568` is named `03_COGS_Supplier_Monthly_Log`. The GID is correct so it works — this is a cosmetic issue.

**`--month` CLI override (v3.4):**
```bash
python3 cogs_parser.py                    # default: current month
python3 cogs_parser.py --month 2026-07    # target specific month
```
Pattern: `argparse` → `--month YYYY-MM` → split → `date(int(y), int(m), 1)`. Fallback: `date.today().replace(day=1)`.

**Month-header format (v3.4):** Entries use `## YYYY-MM` (e.g. `## 2026-07`), changed from `## MM/YYYY` in v3.2. The duplicate check in `run()` must use the same format — mismatch causes double entries.

**Rich `build_entry()` format (v3.4):** The entry now generates 7 sections matching the June manual format:
1. ⚡ Flags — notable items, no-volume warnings, net impact
2. Tổng quan + Net COGS impact
3. Impact by Supplier table
4. Items Tăng Giá — full table (all 46 rows)
5. Items Giảm Giá — savings ≥100k
6. Menu Price Action Required — items >13%
7. Actions — review checklist + data requests

**Percentage values (critical):** GSheet Sheets API returns `"10%"` as string, not 0.10 as float. `to_float()` must strip `%` before conversion:
```python
s = str(val).replace(',', '').replace(' ', '').replace('%', '')
```
Then `pct = 10` means 10%, impact = `pct / 100 * price * volume`.

**No month filtering in GSheet data:** The tab contains ALL months' rows combined. The parser doesn't filter by date column — it relies on checking whether the month header already exists in the log. When GSheet has mixed-month data, the parser writes ALL rows as one cumulative snapshot.

**Manual extraction (Excel not yet in GSheet):**
When data is only in the FM-PUR-06 Excel file:
```python
import openpyxl
wb = openpyxl.load_workbook(r'FM-PUR-06 ... .xlsx', data_only=True)
ws = wb['July']  # month tab
# Columns: B=Item, C=Supplier, D=Unit, E=OldPrice, F=NewPrice, G=% (decimal), L=Volume, M=Impact
for row in ws.iter_rows(min_row=11, values_only=True):
    if not row[0] or not isinstance(row[0], (int, float)): continue
    item = str(row[1] or '').strip()
    if not item: continue
```

**v3.4 changelog:**
- `build_entry()` rewritten from 626-char summary to 8,437-char rich format with 7 sections
- `to_float()` now strips `%` for GSheet Sheets API compatibility
- `--month YYYY-MM` CLI argument for non-current-month targeting
- `month_header` uses `%Y-%m` format (matches new entry headers)
- Removed duplicate `aggregate_changes()` / `fmt_vnd()` / `flag_emoji()` functions
- `calc_impact()` extracted as standalone for clarity
- `defaultdict` imported for supplier aggregation
- `fmt_vnd()` handles zero/null input with `"—"`

## Vault SSOT Sync Wrapper Pattern (update_manpower_master.py)

When a parser output must be merged into a **structured SSOT markdown file** (labeled `## Block N` sections, e.g. `Manpower_Master.md`) rather than a rolling `10_OPERATION_DATA` log, use this wrapper pattern. The wrapper calls an existing parser (e.g. `parse_payroll.py`) and writes a NEW block entry WITHOUT disturbing other blocks.

**File anatomy:** SSOT has `## Block 1` (Warren-authored, NEVER overwritten), `## Block 2` (auto Actual Stock, newest-on-top), `## Block 3` (Gap/Vacancy). Wrapper only touches Block 2.

**Design rules:**
1. **dry-run default, `--apply` to write.** Always show diff preview first.
2. **`--month YYYY-MM` override is MANDATORY for backfill.** Underlying parser (`parse_payroll.py`) fails to detect month from abbreviated filenames ("Apr" ≠ month_map key "april") → returns `month=None`. Wrapper must guess from filename OR accept `--month`. Never fall back to `date.today()` silently for backfill (it mislabels an old month as current). Filename-guess map: `jan/feb/mar/apr/may/jun/jul/aug/sep/oct/nov/dec → 01..12`.
3. **Scope-aware store filtering (OPS + Office).** `parse_payroll` normalizes the office location (e.g. `ltt office`) to `Office` and includes it in the parsed result. For `Manpower_Master.md` the DECIDED scope (2026-07-07, Warren directive) is OPS + Office support (1 Coordinator + 2 Maintenance) = 65 plan — so `STORE_ORDER = [LU3, LU5, LU7, Office]` and Office IS in system totals. Only drop stores that are neither OPS nor Office (truly foreign divisions). RECOMPUTE system totals from the filtered set — do NOT trust `result["system"]` blindly (the underlying parser may retain skipped-non-ops rows). If a future SSOT is genuinely OPS-only, remove `Office` from `STORE_ORDER`; the principle is identical, only membership changes.
4. **Idempotency guard:** skip if `### YYYY-MM` already exists in Block 2 (regex `### {month}\b`). Prevents duplicate on re-run.
5. **Backfill ordering (newest-on-top):** insert-position logic:
   - Backfill month `<` existing → insert BEFORE the first existing month that is NEWER (`if em > month: insert_at = base + pos`).
   - Newest month `>` all existing → insert at TOP (after blockquote doc line).
   - WRONG: inserting at region END for newest month (puts it at bottom). WRONG: `em < month` condition (puts newer month below older).
6. **Single `(latest)` label:** only the MAX month gets `(latest)`. Use `_relabel_latest()` that strips all `(latest)` then re-adds to max month. Run it AFTER insert.
7. **Delta vs prev:** `get_prev_month_json()` must return the month IMMEDIATELY before current (max month `< current`), NOT just "any other month". Otherwise Δ jumps across gaps. **Sign rule (critical, learned 2026-07-07):** Δ must be `current - previous` where `previous` = the OLDER adjacent month. Each month's entry says "vs {prev_month}: {cur} vs {prev} = {cur-prev}". A standalone builder that iterates newest→oldest and treats the next-loop month as "prev" will INVERT the sign (e.g. show May "+3 vs Apr" when May actually DROPPED to 56 from 59). **Fix:** sort entries ascending (Jan→May) for the Delta calc loop, set `prev = (month, active, cost)` each iteration, compute `d = cur - prev`. Then REVERSE the built blocks for newest-on-top display. Verify: May vs Apr must read `-3 active` (56 vs 59), NOT `+3`.
8. **Path safety:** `SCRIPT_DIR = Path(__file__).resolve().parent`; Master at `SCRIPT_DIR.parent / "30_KNOWLEDGE_BASE/..."` (SCRIPT_DIR already = `vault/scripts`, so `.parent` = `vault` — do NOT add another `/vault` segment, or you get `vault/vault/...`).

**Frontmatter `last_updated` regex pitfall (2026-07-07):** When a rebuild script bumps `last_updated`, a regex like `re.sub(r'(last_updated:\s*"?)(...)', r'\1...', ...)` with optional `"?` can EAT the `last_updated: ` prefix if the captured group swallows the quote and the replacement drops it — producing `P26-07-07"` (corrupted YAML). **Fix:** use an exact, anchored replacement that preserves the key: `re.sub(r'last_updated:\s*"[^"]*"', f'last_updated: "{today}"', content, count=1)`. Never make the key-name part of an optional-capture group. After any frontmatter rewrite, assert the YAML still parses (grep for `last_updated:` with a valid date value) before writing.

**Embedded JSON — OPTIONAL; Warren REJECTED it for Manpower_Master.md (2026-07-07):** The general SSOT pattern carries a ```` ```json ```` block for Hermes grep. BUT Warren (non-IT) explicitly said *"tôi ko muốn thấy mấy cái json — nó rối cho tôi"* → for HUMAN-FACING SSOT files (Manpower_Master.md), DO NOT embed fenced JSON. Use markdown tables only; downstream consumers (dashboard generator) MUST parse the markdown tables, not JSON. If a future SSOT genuinely needs machine-grep, isolate JSON in an HTML comment `<!-- data: {...} -->` (zero visual footprint) — never a fenced block in a file Warren opens. Rule of thumb: **if Warren reads the file directly, no fenced JSON.**

**Out-of-scope store handling (LU4 / foreign divisions):** `parse_payroll` may return stores NOT in `STORE_ORDER` (e.g. March 2026 Excel returned `"L'Usine Thao Dien - LU4"`). The wrapper only iterates `STORE_ORDER = [LU3, LU5, LU7, Office]`, so LU4 is silently dropped — that is CORRECT when the SSOT scope is 3 stores + Office (plan 65, no LU4). Verify the dropped store is genuinely out-of-scope (not a mis-normalized LU3/5/7) by checking the parse result stores list in dry-run. If Warren later adds a 4th store, expand `STORE_ORDER` AND `Block 1` plan accordingly.

**Office headcount ramp is normal:** Office staff count per month varies as recruitment completes (March 2026 = 1 Office HC, April/May = 3). This is real data, NOT a parser bug. System totals recompute from the filtered set each month, so month-to-month Office delta is expected. Do NOT "correct" Office to a constant — let the Excel drive it.

**Verification discipline (ad-hoc, temp):**
- Write temp verify script in `%TEMP%` with `hermes-verify-` prefix. Copy Master to temp, run `--apply`, assert: idempotency (count==1), Block 1 preserved, ordering (Aug>May>Apr), latest-label uniqueness (count `(latest)`==1), delta present.
- Assertion pitfall: match `### 2026-05` (NO trailing space) — line is `### 2026-05\n`, so `"### 2026-05 "` (space) fails. Use `"### 2026-05 (latest)" not in c and "### 2026-05" in c`.
- Clean up temp dir after.
- Use REAL source Excel when available (April Excel) for ≥1 dry-run; fixtures only for newer-month/ordering tests. NEVER fake data into the real Master.

**🚨 CRITICAL PITFALL (learned 2026-07-09): never run the writer against the REAL SSOT file during testing.**
`update_manpower_master.py` (and any SSOT-block writer) writes DIRECTLY into the production markdown file.
A test run with a throwaway month (e.g. `--month 2026-07` on a June xlsx) WILL inject garbage ("July")
into `Manpower_Master.md`. This happened in-session: the test wrote a fake July block, and `git checkout --`
was required to recover, then hand-edits had to be re-applied.
**MANDATORY test protocol:** copy BOTH the Master and the xlsx into `%TEMP%`, rewrite `MM_PATH` in a
copied script to point at the temp copy, run with a month NOT in source (e.g. `2026-13`) to bypass the
idempotency guard, assert, then `shutil.rmtree(tmp)`. The real file must NEVER be touched by a test.
See `references/payroll-xlsx-role-breakdown.md` for the full recipe + verified June 2026 role-breakdown numbers.

**Arithmetic discipline (learned 2026-07-09):** when transcribing parser/role totals into the SSOT by
hand, Warren caught `RM1 + FloorLead2 + SA4 = 7` mis-summed as 8. Re-add components before writing
hand-edited summaries. Script-computed totals are safe; hand summaries are not.

**Reference:** `references/ssot-sync-wrapper-pattern.md` for full session detail + verify script template. `references/payroll-xlsx-role-breakdown.md` for payroll-xlsx role parsing (markitdown, COST_IDX=67, Department/Position categorization, test-on-copy protocol).

## MANDATORY VERIFY GATE (Warren rule: never trust LLM, verify everything)

**After EVERY parser run that reads Excel/CSV/PDF** (payroll, HR, CPH, COGS, revenue, grabfood, item sales, wastage, or any xlsx), Hermes MUST run the `verify-parser-output` skill gate BEFORE reporting numbers to Warren or committing output.

Enforcement:
1. After parser writes output → independent recompute (fresh script, different method if possible — markitdown vs openpyxl).
2. Cross-assert EVERY emitted number (totals, per-role, gap, +/-) vs LLM output.
3. Category-drop scan: count raw rows vs filtered rows; flag any Loc=NaN / empty-key row silently dropped (e.g. Operation Admin Coordinator with Loc=NaN → must classify via Dept). **This Loc=NaN → dropped-to-OTHER → fabricated gap is the #1 verify failure in this vault** (caught 2026-07-09: LLM wrote "Maintenance -1" for a full 3/3 office). Always classify by Dept fallback, never Loc alone.
4. Emit `VERIFY_RESULT: PASS|FAIL` + dropped-row count. Temp script `hermes-verify-*.py` in `%TEMP%`, cleaned after.
5. If FAIL → LLM output is WRONG until proven otherwise. Fix the parser logic, re-run, re-verify. Do NOT commit unverified numbers.

This gate is NOT optional. A parser result without a verification report = UNTRUSTED. Load `verify-parser-output` skill for the full 4-step procedure + reusable template.

## Related Scripts and References

- `references/ssot-sync-wrapper-pattern.md` — Vault SSOT sync wrapper (block-structured markdown maintenance: idempotency, backfill ordering, latest-label, Office filter, --month override, ad-hoc verify).
- `references/cph-gsheet-sync-pattern.md` — push CPH from `cph.json` → GSheet `02_MASTER_CPH` (sync_cph_gsheet.py). SSOT chain, SA-key WRITE auth, record-shape gotcha, idempotent upsert, verify recipe.
- `references/static-html-dashboard-pattern.md` — generate interactive Chart.js dashboards from parsed ops data. Pattern: JSON injection → static HTML → browser-viewable. Reusable for COGS, Wastage, any monthly snapshot.
- `references/daily-revenue-report.md` — `vault/scripts/generate_today_revenue.py`, daily cron that fetches COL_Weekly data from the same GSheet, computes WTD revenue tables, writes `today.md`, and sends via Telegram. Shares `fetch_gviz()` infrastructure with all parsers.
- `references/cogs-parser-workflow.md` — full COGS data flow, manual Excel extraction, impact calculation.
- `references/ssot-sync-wrapper-pattern.md` — Vault SSOT sync wrapper (block-structured markdown maintenance: idempotency, backfill ordering, latest-label, Office filter, --month override, ad-hoc verify).
- `references/cph-gsheet-sync-pattern.md` — push CPH from `cph.json` → GSheet `02_MASTER_CPH` (sync_cph_gsheet.py). SSOT chain, SA-key WRITE auth, record-shape gotcha, idempotent upsert, verify recipe.
- `references/static-html-dashboard-pattern.md` — generate interactive Chart.js dashboards from parsed ops data. Pattern: JSON injection → static HTML → browser-viewable. Reusable for COGS, Wastage, any monthly snapshot.

## Downstream Consumers — Index Builders That Depend on Parser Output

When parser format changes (e.g. hourly_cover_parser v4.5 → v5.0), downstream scripts that **read** parser output can break silently — they don't run during the parser's own test suite.

Known downstream consumers:

| Parser Output | Downstream Consumer | Location | Risk |
|--------------|-------------------|----------|------|
| `09_Hourly_Cover_Revenue_Log.md` | `monthly_cover_ingest.py` | `vault/scripts/monthly_cover_ingest.py` | **HIGH** — depends on all 3 data formats (JSON block, Roll-up table, D1 rows). V0.3: JSON parser with warning on malformed data, key fallback, missing-store validation, init-before-loop fix. |

**Pattern for format-resilient index builders:**
1. Add new parser function for the latest format (e.g. `parse_json_block()`)
2. Place it at priority-1 in the extraction chain
3. Keep old parsers as fallbacks (priority-2, priority-3)
4. Always test against ALL known format variants in the log file, not just the latest

**Verification after any parser format change:**
```bash
# 1. Check which scripts read the parser output file
grep -rn '09_Hourly_Cover_Revenue_Log' vault/scripts/ vault/10_OPERATION_DATA/parsers/

# 2. Test each downstream consumer against the new format
python vault/scripts/monthly_cover_ingest.py --dry-run
# Verify all week sections parse correctly (check covers values)
```

### JSON Code Block Parsing — Pitfall Patterns (learned 2026-07-06)

When a downstream index builder reads markdown that contains embedded ` ```json ... ``` ` blocks (like `09_Hourly_Cover_Revenue_Log.md` v5.0 format), these pitfalls apply regardless of the specific parser:

**P1. Accumulator must be initialized BEFORE the loop, not inside the JSON handler.**
```python
# WRONG: json_lines only defined if JSON_BLOCK_RE matches
for line in section['lines']:
    if JSON_BLOCK_RE.match(line):
        in_json = True
        json_lines = []  # ❌ UnboundLocalError if section has no JSON block
        continue
    if in_json:
        json_lines.append(line)

# RIGHT: init at outer scope before loop
json_lines = []
for line in section['lines']:
    if JSON_BLOCK_RE.match(line):
        in_json = True
        # no inner reset needed — outer init is sufficient
        continue
    if in_json:
        json_lines.append(line)
```
The inner reset (`json_lines = []` inside the handler) is only needed if the section can have multiple JSON blocks (uncommon). For single-block-per-section, outer init alone is correct and safer — sections without JSON blocks return `[]` → `{}` naturally.

**P2. Always warn on parse failure — silent fallback corrupts data undetected.**
```python
except json.JSONDecodeError as e:
    print(f'  ⚠ JSON parse failed W{section.get("week_num", "?")}: {e}')
    return {}
```
Without this warning, malformed JSON silently falls through to an older parser format (roll-up table, D1 row). The operator sees output but has no way to know the source was different.

**P3. Key fallback for upstream format evolution.**
```python
covers = s.get('c') or s.get('covers') or 0
```
If the upstream format renames `c` to `covers`, this degrades gracefully instead of silently returning 0.

**P4. Validate expected entities when JSON is present.**
```python
known = {'LU3', 'LU5', 'LU7'}
found = set(result.keys())
if found and found != known:
    missing = known - found
    print(f'  ⚠ JSON block for W{section.get("week_num", "?")} missing: {", ".join(sorted(missing))}')
```
A partial JSON block (only 1-2 stores) currently **overrides** the fallback parsers — because a non-empty dict from `parse_json_block()` short-circuits the priority chain. Without validation, the missing stores are silently lost.

**5. Priority chain design:**
```
JSON data block (most reliable) → Roll-up table (structured) → D1 fallback (older format)
```
Higher priority parsers should return `{}` (empty/falsy) when they can't produce complete data, so the chain falls through. A non-empty but partial result from a high-priority parser will block lower-priority parsers — validate completeness before returning.

### Restoring compressed data from dashboard HTML (2026-07-06 session):
When a weekly log entry is compressed (`<!-- Compressed — data archived in dashboard HTML. -->`), the dashboard HTML embeds raw data in a JavaScript `WEEKS` array. Extract via:
1. Open `vault/30_KNOWLEDGE_BASE/wiki/09_hourly_cover_revenue/dashboard.html`
2. Find `var WEEKS = [{...}]` — each element has per-store covers, revenue, rpc
3. Add a `### 📊 Data` + JSON block to the compressed week section
4. Run the downstream consumer to verify extraction

## Accumulation Data Rot Prevention

**Problem:** JSON accumulation files (`_accumulation/item_sales.json`) accumulate stale week keys when the week-ID format changes between script versions. Old-format keys (e.g. `"2026-W22"`) persist alongside new-format keys (`"W26"`) — they bloat the file, pollute `_metadata.weeks`, and can create phantom months in `_metadata.months`.

**Canonical signal:** `week["items"]` is `{}` (empty dict) or missing. The `items` field is the only meaningful payload — empty items means the entry is a leftover from a previous format that wrote different fields (`stores`, `top_food`, etc.).

**Canonical fix — auto-clean at load time:** Add this block immediately after loading the accumulation JSON (before writing new data):

```python
orphan_ids = [k for k in accum["weeks"] if not accum["weeks"][k].get("items")]
for k in orphan_ids:
    del accum["weeks"][k]
if orphan_ids:
    print(f"  Cleaned {len(orphan_ids)} orphaned week entries: {orphan_ids}")
```

**Then rebuild metadata from reality:**
```python
accum["_metadata"]["weeks"] = sorted(accum["weeks"].keys())
months = set()
for wid, wdata in accum["weeks"].items():
    if wdata.get("week_start"):
        months.add(wdata["week_start"][:7])
accum["_metadata"]["months"] = sorted(months)
```

This prevents stale metadata (`_metadata.months` containing phantom months) from causing downstream issues.

**One-time cleanup (existing file):** Run a Python one-liner that removes keys with empty `items`, then writes back. No need for a dedicated script — the auto-clean in subsequent `--accumulate` runs will handle it going forward.

**Key insight:** `bool({}) == False` — the empty-dict check works for both missing `items` key and existing-but-empty items dict. No need for explicit `len()` or `is None` checks.

### Menu GP Monthly — Accumulation Cadence, Sheet-No-History Pitfall & Read-Only Probe (2026-08-03)

`menu_gp_parser.py` (at `vault/scripts/`, NOT `parsers/`) drives `14_Menu_GP_Monthly_Tracker.md` from accumulated Star Horse weekly item sales. Two durable facts learned this session:

**F1 — Star Horse GSheet retains ONLY the current week's column. No history.**
Verified 2026-08-03: sheet has 21 columns but exactly ONE week column (`history_11_... Period: from 7/6/2026 to 7/12/2026` = W28). Columns for 7/13, 7/20, 7/27, 8/2 → 0 matches. The GSheet rolls forward; past weeks vanish.
→ **Consequence:** `--accumulate` MUST run once per week WHILE that week is live (e.g. W29=13/7, W30=20/7, W31=27/7). If a week is skipped, its data is permanently lost for the month — the monthly parse cannot backfill it later because the sheet no longer has it.
→ **Monthly parse timing:** The monthly job (calendar: 1st Monday, e.g. Aug 3 for July) runs AFTER the sheet has rolled to next month's week. It reads `_accumulation/item_sales.json`, NOT the sheet. So the JSON must already hold all 5 July weeks. If any week is missing → `load_accumulated_month` returns 0 items → dry-run prints `Accumulated: N weeks, 0 unique items` → **ABORT, do not write.** (This is how the July gap was caught 2026-08-03: only W28 present → 0 items.)

**F2 — Accumulation format-rot is repairable by re-accumulating WHILE the sheet is still on that week.**
A prior `--accumulate` (2026-07-13) wrote W28 in an OLD format: `{week_start, stores:{LU3/LU5/LU7/System with qty/rev}}` — NO `items` per-item dict. `load_accumulated_month` iterates `wdata.get("items", {})` → empty → 0 items even though the week "exists". The auto-clean in `accumulate_week()` only removes keys with empty `items`, so a store-only key survives as a silent blocker.
→ **Repair (confirmed 2026-08-03):** when the sheet is STILL on that week, re-run `--accumulate`. It overwrites the key with the correct per-item `items` dict (158 items for W28). After repair, dry-run shows `Accumulated: 1 weeks, 158 unique items` and `months` gains the missing month.
→ **Do NOT repair via hand-edited JSON** — always re-run the parser against the live sheet.

**Read-only probe BEFORE any write (mandatory when investigating gaps):**
Inspect sheet state without touching `item_sales.json`:
```bash
cd C:/Users/khoans/Documents/Warren_OS_Local/vault/scripts
python3 -c "from menu_gp_parser import fetch_star_horse, detect_week_id; parsed, cols = fetch_star_horse(); wid, ws = detect_week_id(cols); print('WEEK:', wid, ws, '| items:', len(parsed)); import re; print('future-week cols:', [c for c in cols if re.search(r'(7/13|7/20|7/27|8/2)/2026', str(c))])"
```
This calls `fetch_star_horse()` + `detect_week_id()` only — never `accumulate_week()` — so no vault write. Use it to confirm: (a) which week the sheet is on, (b) item-row count (should be ~390 for a full week), (c) whether future-week columns exist (if yes, sheet still holds history — rare).

**Runbook gap + Warren's pasteable-block preference:** The calendar runbook for Menu GP Monthly lacked the `--accumulate` step in "CÁCH CHẠY" — it only said "accumulate đủ weeks" without the command. Warren prefers pasteable command blocks over runbook `.md` files (see Documentation preference). Give him these two blocks instead of editing the calendar description:

Weekly (paste every Monday, while week is live):
```
MENU GP WEEKLY ACCUMULATE — W<XX>
cd /c/Users/khoans/Documents/Warren_OS_Local && python3 vault/scripts/menu_gp_parser.py --accumulate
→ check: "✅ Accumulated week W<XX>" + total weeks increments. If "Cannot detect week" → skip, báo Hermes.
```

Monthly (1st Monday, e.g. Aug 3 for July):
```
MENU GP MONTHLY — 2026-07
cd /c/Users/khoans/Documents/Warren_OS_Local
1. python3 vault/scripts/menu_gp_parser.py --month 2026-07 --dry-run
2. python3 vault/scripts/menu_gp_parser.py --month 2026-07
3. python3 vault/scripts/gen_menu_gp_dashboard.py
→ xem 14_Menu_GP_Monthly_Tracker.md + open dashboards/menu_gp_trend.html
→ nếu delta >5% vs RevLog → 🔴 BLOCKED, dừng, báo Hermes
```
Note: run from repo root `C:/Users/khoans/Documents/Warren_OS_Local` (menu_gp_parser resolves VAULT_ROOT from `__file__`, and imports `_utils` from `scripts/`). Use `C:/Users/...` not `/c/Users/...` (MSYS path quirk).

**Raw evidence + JSON before/after:** see `references/menu-gp-accumulation-cadence.md`.