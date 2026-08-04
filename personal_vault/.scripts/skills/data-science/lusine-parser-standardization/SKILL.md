---
name: "lusine-parser-standardization"
description: "Standardized pattern for L'Usine operational parsers with self-maintaining property tables (YAML frontmatter)"
category: "data-science"
version: "1.5"
---

# L'Usine Parser Standardization Skill

Standardized pattern for L'Usine operational parsers with self-maintaining property tables (YAML frontmatter).

## Core Pattern

Every parser follows this structure:
1. **PROPERTY_DEFAULTS** dict extending `PROPERTY_DEFAULTS_BASE`
2. **run_parser_with_frontmatter()** from `_frontmatter_base` handles all I/O
3. **Automatic sync** - reads frontmatter at startup, writes updated frontmatter on every run

## Property Table Schema (YAML frontmatter)

```yaml
name: string
type: tracker
status: active
owner: Warren (Head of Ops)
stores: [LU3, LU5, LU7]
data_source:
  sheet_id: string
  sheet_name: string
  gid: string
  parser: string (relative path)
  parser_version: string
refresh_cadence: "Mon 09:45 (auto via Hermes cron)"
cross_refs: [list of related log files]
key_definitions: {metric: formula}
targets: {threshold_name: value}
last_updated: date (auto-synced)
```

## Implementation Checklist for New Parsers

- [ ] Define `PROPERTY_DEFAULTS` extending `PROPERTY_DEFAULTS_BASE`
- [ ] Set `PARSER_VERSION`, `SHEET_ID`, `SHEET_GID`, `LOG_FILE`
- [ ] Implement `fetch_sheet()` returning raw rows
- [ ] Implement `parse_rows()` / `filter_week()` returning structured data
- [ ] Implement `build_entry(week_start, week_end, data)` returning markdown
- [ ] Call `run_parser_with_frontmatter()` with all required functions

## Key Files

- `scripts/modules/_frontmatter.py` - Core YAML utilities (read, write, validate, deep_merge)
- `scripts/modules/_frontmatter_base.py` - Standardized parser runner with frontmatter sync

## Auto-sync Behavior

Every parser run:
1. **Reads** frontmatter via `validate_and_sync_frontmatter()`
2. **Validates** against `PROPERTY_DEFAULTS` (merges missing keys)
3. **Syncs** dynamic fields: `parser_version`, `sheet_id`, `gid`, `last_updated=today`
4. **Writes** frontmatter + body via `write_frontmatter()`

## Pitfalls & Fixes

> **Top 8 most common pitfalls.** Full catalog (50+ entries): see `references/pitfalls.md`

| Issue | Fix |
|-------|-----|
| **GSheet merged cells → empty values** | Implement **forward-fill**: track `current_item_group`, update when cell has value, inherit when empty. Skip "Total" rows. See `references/gsheet-merged-cells-forward-fill.md` |
| **Revenue display truncation: `int(value/1e6):.1f`** | `int()` truncates toward zero → loses up to 999,999 VND per store. **Fix**: remove `int()`, let `:.1f` round naturally: `f"{sys_r/1e6:.1f}tr"`. |
| **Markdown table column alignment (pipe count)** | Count `|` on header row vs data row. Missing closing pipe on first column shifts all data by one column. |
| **Missing table separator row (`---|---|---|`)** | Every markdown table needs a header separator line. Auto-fix: `f"|{'---|' * col_count}"` after header. |
| **HTML dashboard gen: f-string + JS `${}` conflict** | Use `.replace()` on static `_TEMPLATE` string with `{PLACEHOLDER}` markers instead of f-strings. |
| **`infer_category()` display vs price-target use** | `infer_category()` is for **price targets only** (Item Flags). **NEVER** use for display. |
| **CRLF `---created:` gluing bug (backfill trap)** | Never slice `txt[:3]`. Use `write_frontmatter()` helper. Regex match `---
?
` for injection. |
| **`created` frontmatter field: auto-inject ONCE, never overwrite** | `validate_and_sync_frontmatter()` MUST set `created` on first write and PRESERVE it on every re-run. |
| **Dry-run / test preview writes to visible `_inbox` → Obsidian clutter (ROOT-CAUSED 2026-07-27)** | Parser `--dry-run` MUST write preview/scratch files to the HIDDEN dotfolder `._verify_tmp/` (e.g. `LOG_FILE.parent / "._verify_tmp" / f"preview_{wid}.md"`), NOT `_inbox`. A visible `_inbox` under `10_OPERATION_DATA/` shows as junk in Obsidian. Root cause: `hourly_cover_parser.py:711` + `hourly_cover_sql_parser.py:604` did `LOG_FILE.parent / "_inbox" / ...mkdir()` on every dry-run → created orphan empty folder (07:48 daily W29 regen) that Warren saw as trash. FIX (approved): repoint to `._verify_tmp/`. ALSO: delete the scratch file IMMEDIATELY after the dry-run prints — never leave it lying around. |

## Vault-wide `created` backfill (2026-07-13)

Warren repeatedly forgets to add `created:` to vault markdown. A session found 91/226 `.md` with frontmatter missing it. Recover pattern:

1. **Scan** all `*.md` with frontmatter, list those missing `created:`.
2. **Date source** per file (in priority): (a) `last_updated` in the same frontmatter, (b) `git log --reverse --diff-filter=A --name-only --format=%x00%ad --date=short` → first-add date (one git call, not per-file `git log --follow` which is slow on 378 files), (c) fallback `2026-01-01`.
3. **Inject safely** — regex match the opening `---` line, insert `created: <date>\n` after it. NEVER `txt[:3] + ...` (CRLF glue bug above).
4. **Verify** — `yaml.safe_load` on every touched file's frontmatter; assert 0 parse failures and 0 `---created:` glued lines.
5. **Harden so it never recurs** — `_frontmatter.py` `validate_and_sync_frontmatter()` auto-injects `created` on first write + preserves on re-run; `pre_edit_checklist.md` §2 lists `created` as a mandatory frontmatter field.

**Note:** a `git reset --hard` used to undo the buggy backfill also destroyed the `_frontmatter.py` hardening that was in the same commit — had to re-apply + re-verify + force-push. Undo surgically.

## Dry-Run / Test File Hygiene (Warren rule, 2026-07-27)

**Rule (durable, Bố approved):** Mọi file test / dry-run / preview PHẢI ghi vào `._verify_tmp/` (hidden dotfolder — Obsidian auto-ẩn), và **làm xong PHẢI xoá**.

### Why
- Obsidian hiển thị mọi folder KHÔNG có dấu chấm `.` đầu. Một `_inbox` (visible) tạo ra bởi dry-run = rác trong file explorer, Warren thấy ngay và ghét.
- `._verify_tmp/` (tạo 10/07) đã tồn tại, ẩn mặc định → đúng chỗ chứa scratch.

### Pattern
```python
# WRONG (creates visible junk in Obsidian):
prev_path = LOG_FILE.parent / "_inbox" / f"preview_{wid}.md"
prev_path.parent.mkdir(parents=True, exist_ok=True)
prev_path.write_text(preview)
# (file left behind → orphan clutter)

# RIGHT (hidden, auto-cleaned):
prev_path = LOG_FILE.parent / "._verify_tmp" / f"preview_{wid}.md"
prev_path.parent.mkdir(parents=True, exist_ok=True)
prev_path.write_text(preview)
print(f"[DRY-RUN] Preview -> {prev_path}")
# ... after run completes:
prev_path.unlink(missing_ok=True)   # DELETE scratch when done
```

### Applies to
- `--dry-run` / `--dry` flags in any vault parser (hourly, COL, item sales, etc.)
- Any temp verify artifact, preview markdown, debug dump
- Test fixtures the parser generates during a probe

### Enforcement
- Before creating any scratch file in a parser, ask: "Is this going to `._verify_tmp/` AND will I delete it after?" If no → violate.
- Never hand Warren a dry-run result that leaves a visible file behind.

## Multi-Source Parser Pattern (Deterministic Verify)

When a parser combines data from MULTIPLE sources (GSheet + vault markdown), use this pattern:

### Architecture
```
Source A (GSheet) -> fetch() -> dict
Source B (markdown) -> fetch() -> dict
Source C (markdown) -> fetch() -> dict
calculate(A, B, C) -> result + deterministic checks
verify() -> pass/fail
output() -> JSON or markdown
```

### COGS → Recipe Cost Propagation

When a monthly parser needs ingredient price adjustments (like `menu_gp_parser.py`), see `references/cogs-recipe-cost-propagation.md` for the full technique: building an ingredient→recipe index, parsing percent changes from COGS log pipe tables, proportional cost adjustment, deep copy discipline, and name normalization for bilingual (English/Vietnamese) ingredient names.

### Step Structure
```
[1/N] fetch_source_a()
[2/N] fetch_source_b()
[N/N] calculate() + verify()
```

### Deterministic Verification
```python
checks = {
    "formula_1": abs(regular + ot - total) < 0.1,
    "dept_sum": abs(foh+boh+cleaner - total) / total < 0.01,
    "ratio": abs(ot_ratio - ot/total*100) < 0.1,
}
# all() check before writing output
```

### Pitfalls
- **OT markdown has 2+ table formats**: Write parser to handle both old (extra Staff column) and new format.
- **Covers may be incomplete for older months**: Hourly covers file starts from W14 (March end). Earlier months need fallback source.
- **Headcount: use Active, not On Payroll**: Payroll files have both. Always use Active (second number) for Hrs/Emp.
- **Temp verify scripts**: Write to Temp, run, rm. Never keep in vault.
- **Pass `--month`**: Never hardcode. Every multi-source parser must accept `--month YYYY-MM`.

## Weekly-to-Monthly Aggregation Pattern

When a parser aggregates **weekly vault markdown data** into a **monthly wiki index** (no GSheet source), use this pattern:

### Data Flow
```
Source (vault markdown) → parse_weekly_sections() → group_by_month() → calculate() → verify() → write_index()
```

### Data Source Layout

| Element | How to find |
|---------|-------------|
| **Week sections** | `## 2026-W## \| <date_range>` — anchor for each week |
| **JSON data block** | `### 📊 Data` + `` ```json `` block → v5.0 compact format. Contains `stores[].c` (actual covers per store). **Priority #1** when present. |
| **Weekly Roll-up table** | `### Weekly Roll-up (Δ vs W##)` → contains `\| Store \| Actual Covers \|` — preferred source for per-store cover totals |
| **D1 row (fallback)** | `\| **D1** \| **day1** \| ... \| **week_total** \|` in `\#\#\# <Store> -- Hourly Covers` — use when Weekly Roll-up table is absent (older weeks) |
| **Peak hour (12h)** | Row `\| 12 \| ... \| **week_peak_sum** \|` in `### <Store> -- Hourly Covers` section |
| **Date range** | Extracted from week heading — 3 formats: `DD/MM–DD/MM/YYYY`, `YYYY-MM-DD -> YYYY-MM-DD`, single date |

**Order matters.** The weekly log may have multiple data sources in the same section (v5.0 JSON block + hourly D1 rows + legacy roll-up). Parse in this order:

1. **JSON data block** (`### 📊 Data` → `` ```json ``) — v5.0 compact format, `stores[i].c` = actual covers. Fastest, most reliable, no regex. **Skipped if absent.**
2. **Weekly Roll-up table** (`### Weekly Roll-up`) — parsed column map with `| Store | Actual Covers | Gross Covers | Split | ...`. **Skipped if absent.**
3. **D1 fallback** — `| **D1** |` or `| **Sum** |` rows in per-store hourly tables

**Implementation (Python):**
```python
def extract_covers(section):
    # Priority 1: JSON data block
    json_data = parse_json_block(section)
    if json_data:
        return json_data
    # Priority 2: Weekly Roll-up table
    if has_rollup_table(section):
        data = parse_rollup_table(section)
        if data:
            return {k: v['actual_covers'] for k, v in data.items() if k != 'System'}
    # Priority 3: D1 fallback
    return parse_d1_fallback(section)
```

### Month Grouping Logic

**CRITICAL — weeks can span two months (e.g. W18 crosses April→May).** Do NOT assign a week to a month by week number alone.

**Pattern:** Extract daily covers from each store's hourly table D1 row (day-by-day columns), sum day-by-day within calendar month boundaries.

Fallback: if D1 daily breakdown is unavailable, use the week's date range to determine which month has the majority of the week's days and assign the *entire* week total to that month. Document the approximation.

### Calculation Pattern

```python
# 5 output sections:
# 0. Executive Summary — System Covers | Avg Rev/Cover | Best Store | Worst Store | Peak 12h | 12h%
#    Columns: month + Apr/May/Jun + Q2 + YTD (where applicable, else '—')
# 1. System Cover Summary — month + LU3 + LU5 + LU7 + System + Δ MoM% + Notes
# 2. Average Covers per Day — month + LU3 + LU5 + LU7 + System + Days-in-month
# 3. System Peak Hour (12h) — month + LU3 + LU5 + LU7 + System 12h + % of Daily Total
# 4. Revenue per Cover — month + LU3 + LU5 + LU7 + System (in k VND)
#
# Δ MoM formula: (current - prev) / prev * 100  (System Δ Use system total only)
# Rev/Cover = monthly Net Revenue sum / monthly Actual Covers sum
# Rev/Cover source: Weekly Roll-up table (Net Revenue + Actual Covers per store per week)
```

### Deterministic Verification

```python
checks = {
    "lu3_lu5_lu7_eq_system": abs(lu3 + lu5 + lu7 - system) < 1,     # REQUIRED
    "revlog_crosscheck": abs(monthly_cover_parser - revlog_covers) / revlog_covers < 0.05,  # OPTIONAL — report, don't block
    "peak_pct_is_12h_of_total": abs(peak_12h / system * 100 - peak_pct) < 0.5,
}
```

### Pitfalls

| Issue | Fix |
|-------|-----|
| **Week heading format varies — 3 variants** | Write a `_parse_date_range(header)` helper that tries ISO first (`YYYY-MM-DD -> YYYY-MM-DD`), then DD/MM (`DD/MM–DD/MM/YYYY`), then falls back to single date. **Em dash (`–`) is Unicode U+2013 — split on it, not hyphen.** |
| **Weekly Roll-up table missing in older weeks** | Weeks before W24 (2026-06-08) may not have roll-up tables. Fallback: parse D1 row from `### <Store> -- Hourly Covers` sections. D1 Wk Sum = per-store weekly actual covers. |
| **12h peak spans all stores — extract from ALL hourly table** | The `### ALL -- Hourly Covers` section has a `\| 12 \| ... \| **week_total** \|` row. This contains sum of 12h covers for system. If ALL section is missing, sum `\| 12 \|` rows from individual LU3/LU5/LU7 sections. **Split issue: the `\| 12 \|` row uses MAKEDOWN BOLD on Wk Sum (bold \*\*) — other fields are plain.** |
| **Cross-check against RevLog** | Compare monthly actual covers against `01_Weekly_Revenue_Log.md`. Parse `\| <store> \| <week_end> \| \d+ \|` patterns. Use ±5% tolerance. Report mismatches in delta, don't block. |
| **MTD section in weekly log is rolling — not reliable** | The `### MTD - Tháng X/YYYY` section in the weekly log only reflects latest written week, not full month aggregate. Do NOT use as monthly source. |
| **Commas in numbers** | `\| LU3 \| 1,234 \|` — strip commas before int conversion: `int(val.replace(",", ""))`. |

### Output: Delta Report

Before writing to monthly index, print delta to console:

```text
== Monthly Cover Aggregation Delta ==
Month: 2026-05
  LU3:  X covers (Δ Y% vs Apr)
  LU5:  X covers (Δ Y% vs Apr)
  LU7:  X covers (Δ Y% vs Apr)
  System: X covers (Δ Y% vs Apr)
  Peak 12h: X covers (Y% of daily total)
  Avg/day: X covers
  Cross-check RevLog: OK / MISMATCH (±Z%)
  Holiday contamination: None / <list>
```

### Monthly Cover Ingest — Specific Template

When creating `monthly_cover_ingest.py`:
- Input: `10_OPERATION_DATA/09_Hourly_Cover_Revenue_Log.md` (read-only)
- Output: `30_KNOWLEDGE_BASE/wiki/04_labour_costs/Covers_Hourly_2026_Monthly_Index.md`
- CLI: `--month YYYY-MM` (default: latest complete month)
- Flags: `--dry-run` (show delta, no write), `--force` (overwrite existing month row)
- Data sources within weekly log: Weekly Roll-up table (preferred), D1 row (fallback)
- Cross-check source (optional/pro forma): `01_Weekly_Revenue_Log.md` — monthly aggregation does NOT require external cross-check because the weekly log already validates itself internally against RevLog each week. Warren's explicit preference.
- See `references/covers-weekly-to-monthly.md` for session-specific detail and data anatomy.

## Compact Weekly Format with Machine JSON Block (60/40 Design)

A format optimization for weekly log files targeting **60% machine-readability / 40% human-actionability**. Cuts token count ~50% while making data faster to grep. Successfully implemented in `col_weekly_parser.py` v4.0, `item_sales_parser.py` v2.0, and `hourly_cover_parser.py` v5.0.

### When to Use

- Weekly log has 3+ store detail tables with repeated headers (token waste)
- Current format has a long Flags section re-stating data already in tables
- Hermes needs to grep weekly aggregates without parsing markdown tables
- User explicitly asks for less verbose, more machine-friendly output

### Pattern Structure

```markdown
## 2026-W27 | 29/06-05/07/2026

### 📋 Executive Summary (3 bullets — REQUIRED per Warren preference)
- **System:** COL% 19.6% 🟡 | 18/18 pass | 1.862h total | 496,1tr rev
- **Top concern:** LU3 21,3% 🔴 - revenue -22% nhưng hours chưa điều chỉnh
- **Key Takeaway:** 1+ store vượt ngưỡng đỏ - cần hành động ngay

### 📋 Scorecard
| Store | Rev(M) | Hrs | COL% | SPLH(k) | Δ Rev% | Δ COL | Pass |
|-------|--------|-----|------|---------|--------|-------|------|
| **LU3** | 166.8 | 716 | 21.3🔴 | 233 | -21.8 | +X.X | 6/6 |
| **Sys** | 496.1 | 1862 | 19.6🟡 | 268 | -20.8 | +X.X | 18/18 |

### 📅 Daily Heatmap (1 table replacing N store detail tables)
| Day | LU3 | LU5 | LU7 | Sys |
|-----|-----|-----|-----|-----|
| T2  | 23.5🔴 | 25.1🔴 | 22.0🔴 | 23.5🔴 |

### ⚡ Key Flags (max 3, analytical insight NOT data re-statement)
- LU3: 6/7🔴 — Revenue -22% W/W nhưng hours flat → COL crisis

<!-- col_data: {"week":"2026-W27","sys":{"rev":496.1,"hours":1862,"col":19.6,...},"stores":{"LU3":{...},"LU5":{...}},"daily":{"LU3":{"T2":23.5,...}}} -->
```

### Design Rules

| Rule | Detail |
|------|--------|
| **Scorecard** | 1 table = stores + System row. Δ columns vs prev week. Status emoji inline in metric cell (no separate Status column). Compact unit notation: `Rev(M)`, `SPLH(k)`. |
| **Heatmap** | 1 table thay N store detail tables. Chỉ metric chính (COL%). Day names dạng T2/CN. System column = weighted avg across stores. |
| **Key Flags** | Max 3 bullets. Analytical (cause + effect), NOT data re-statement. No "🔴 LU3 T4 26.6%" — use Flags section for insight, not data. |
| **Machine Block** | HTML comment `<!-- col_data: {JSON} -->`. Hermes grep 1 dòng = all weekly numbers. JSON schema: `{week, range, sys:{rev,hrs,col,splh,pass,d_rev,d_col}, stores:{LU3:{rev,hrs,col,splh,pass,daily:{T2:col,...}}, LU5:{}, LU7:{}}}`. Put all day-system data under `sys` and per-store daily under `stores[store].daily`. |
| **No em dashes** | Use `-` or `,` instead of `—` (U+2014) in all vault output. |
| **No redundancy** | Scorecard + Heatmap + 3 Flags covers all. Remove standalone Flags section (replaced by Heatmap weekend colors + 3 analytical bullets). |

### Token Comparison

| Section | Old (verbose, 3 stores) | New (compact) |
|---------|------------------------|---------------|
| Executive Summary | 4 lines | 4 lines (kept per Warren) |
| Flags list | 10-15 lines | — (replaced) |
| Scorecard | 9 lines | 9 lines (similar) |
| Store detail tables | 9x3 = 27 lines | 8 lines (single heatmap) |
| Key analytical flags | — | 3 lines |
| Machine JSON block | — | 1 line |
| **Total** | **~50-55 lines** | **~25 lines (~50% savings)** |

### Implementation Pattern

```python
def build_entry(week_start, week_end, parsed_rows, prev_parsed_rows):
    # 1. System totals
    sys_rev = sum(...)
    # 2. Executive Summary (3 bullets)
    L.append("### Executive Summary")
    L.append(f"- **System:** ...")
    # 3. Scorecard table (store data + System row)
    L.append("### Scorecard")
    L.append("| Store | Rev(M) | Hrs | COL% | SPLH(k) | D Rev% | D COL | Pass |")
    # 4. Daily Heatmap (single loop over day_order)
    L.append("### Daily COL%")
    L.append("| Day | LU3 | LU5 | LU7 | Sys |")
    # 5. Key Flags (analytical, not re-statement)
    L.append("### Key Flags")
    # 6. Machine JSON block
    L.append(build_json_block(week_id, date_range, aggs, parsed_rows, prev_aggs))
    L.append("---")

def build_json_block(week_id, date_range, aggs, parsed_rows, prev_aggs):
    import json
    stores = {}
    for a in aggs:
        daily = {DAY_SHORT[d["day"]]: round(d["col_pct"], 1) for d in a["days"]}
        stores[a["store"]] = {
            "rev": round(a["rev"] / 1e6, 1),
            "hrs": round(a["hours"]),
            "col": round(a["col"], 1),
            "splh": round(a["splh"] / 1000),
            "pass": f"{a['pass']}/{a['total']}",
            "daily": daily
        }
    return f"<!-- col_data: {json.dumps(data, ensure_ascii=False)} -->"
```

### Relationship to Template Block

The Compact format still requires a `<!-- HERMES TEMPLATE -->` block documenting exact section order. The template block remains SSOT for format rules; this section explains the design philosophy and when to choose this variant.

### Hourly Cover Variant (v5.0) — Revenue Unit M + Decision Board

When applying the 60/40 pattern to **hourly cover & revenue data** (`09_Hourly_Cover_Revenue_Log.md`), the format differs from COL v4.0 because hourly data needs store-level tables, not just a system heatmap.

**Key differences from COL compact format:**

| Element | COL v4.0 | Hourly Cover v5.0 |
|---------|----------|-------------------|
| Revenue unit | M (triệu) | **M** — NOT k (thousands). `round(val/1e6,1)` with `M` suffix. E.g. `2.8M` replaces `2759k` |
| Core tables | Single COL% heatmap (7d x 4 stores) | **Per-store hourly tables** (3 tables, covers·revenue combined) |
| Decision Board | Embedded in Key Flags | **Separate `🔥 DECISION BOARD` table** with 🟢🟡🔴 flags + FBM recommend column |
| Machine block | HTML comment `<!-- col_data -->` | **Visible ```json``` code block** — Hermes parses from JSON directly, no regex |
| Exec Summary | 3 bullets | **3 bullets REQUIRED** (Warren preference) — System | Top/Bottom | Key Takeaway |
| ALL system table | Not applicable | **Dropped** — derivable from 3 stores (~18 lines/tuần saved) |
| Cross-check | ±5% gate | **Dropped unless >2% discrepancy** |
| Conversion boilerplate | In frontmatter | **In frontmatter only** — never repeated per week |
| Dashboard link | Separate file | **Embedded link** at section bottom for 1-click open |

**Decision Board format:**
```markdown
### 🔥 DECISION BOARD
| Flag | Store | Detail | 🧑‍🍳 FBM Recommend |
|------|-------|--------|-------------------|
| 🟢 | LU5 | Rev/cover 269k cao nhất | "Maintain pricing strategy" |
| 🟡 | LU7 | Covers -8% W/W | "Check evening staffing" |
| 🔴 | LU3 | R/1k 10.6 crisis | **"Upsell lunch combo"** |
```

**JSON schema (visible code block):** Contains arrays of hourly covers + revenue per day per store. Hermes reads this block for fast data retrieval without parsing markdown tables.

**Older week compression:** Weeks before the current format retrofitted as JSON-only (keep week header + JSON block, drop markdown tables). Saves ~120 lines/week → ~15 lines/week.

**GSheet column layout:** The Hourly_Revenue tab has non-uniform day columns due to merged cells. See `references/gsheet-hourly-revenue-column-layout.md` for exact column indices, row structure, and the cross-check protocol.

**First implementation:** See `_cases/active/Hourly_Cover_Revenue_Log_v5.0_Spec.md` + `Hourly_Cover_Revenue_Log_v5.0_Plan.md` for full schema, edge cases, and k→M conversion matrix.

### Example Files

- `07_COL_Weekly_Log.md` v4.0 — first implementation of 60/40 compact (Scorecard + COL% Heatmap + JSON block)
- `09_Hourly_Cover_Revenue_Log.md` v5.0 — hourly cover variant (JSON block + Decision Board + unit M)
- `11_Item_Sales_Weekly_Log_Star_Horse_Tracker.md` v2.0 — item sales variant (hidden JSON block, per-store groups top-80%, BCG quadrants, FBM recommendation)

## write_index: Section-Anchored Rebuild Pattern

When updating a wiki-index file (no frontmatter, multiple independent tables), avoid the fragile state-machine approach (4+ boolean flags). Instead:

1. **Find** the target table by its header line
2. **Insert** new rows immediately after the header separator
3. **Skip** the original file's rows that belong to that table (but NOT rows in OTHER tables)
4. **Preserve** everything else (other sections, YTD rows, notes, related links)

```python
# Pseudocode for section-anchored rebuild:
in_table = False
table_written = False
for line in lines:
    if in_table and '|---|---' in line:       # header separator
        output.append(line)
        for new_row in new_rows:
            output.append(new_row)             # insert new data
        table_written = True
        in_table = False
        continue
    if table_written and is_month_row(line):   # skip original rows
        continue
    if is_table_header(line):
        in_table = True
    output.append(line)
```

This pattern was used to fix `write_index()` in `monthly_cover_ingest.py` v0.1. See `references/covers-weekly-to-monthly.md` § Common Bugs & Fixes for the 6 bugs this approach solved.

## Monthly Calendar Reminder for Operational Tasks

Monthly operational parsers (COGS, Wastage, Extra Hours, Menu GP) benefit from a **recurring Google Calendar event** fired on the data-arrival day (typically the 5th of each month).

### Pattern

```python
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

event = {
    'summary': '📊 COGS/Wastage — Ingest file CFO',
    'description': '''Detailed instructions for the monthly task.
Include: data source, CLI commands, expected output files.''',
    'start': {'dateTime': '2026-07-05T10:00:00+07:00', 'timeZone': 'Asia/Ho_Chi_Minh'},
    'end': {'dateTime': '2026-07-05T10:30:00+07:00', 'timeZone': 'Asia/Ho_Chi_Minh'},
    'recurrence': ['RRULE:FREQ=MONTHLY;BYMONTHDAY=5;COUNT=12'],
    'reminders': {
        'overrides': [
            {'method': 'popup', 'minutes': 60},
            {'method': 'email', 'minutes': 1440},
        ],
    },
}
created = service.events().insert(calendarId='nguyen.s.khoa@gmail.com', body=event).execute()
```

- Calendar ID: `nguyen.s.khoa@gmail.com` (Warren's primary calendar)
- Time: 10:00-10:30 GMT+7 (30 min slot — enough to forward file)
- Recurrence: monthly on day 5, 12 occurrences
- Description must include full CLI commands and expected outputs so Warren can act without asking Hermes
- Reference: `10_Wastage_WriteOff_Monthly_Log.md` for the canonical example

## Verification

After implementing new parser:
```bash
cd /path/to/project && PYTHONPATH=... python ../../parsers/your_parser.py
# Should output: "Written -> log.md (parser vX.Y, last_updated=YYYY-MM-DD)"
```

## Completed Parsers (v1.1+)

### Standard (GSheet → Markdown Log)
- `hourly_cover_parser.py` v4.4 - `09_Hourly_Cover_Revenue_Log.md`
- `lto_parser.py` v1.1 - `04_LTO_Weekly_Log.md`
- `grabfood_parser.py` v1.4 - `06_GrabFood_Weekly_Log.md` (v1.4: Executive Summary 3 bullets below week header. v1.3: Channel Mix %, recommendation engine, compact format -70% tokens, nested JSON brace counter fix in `load_prev_week_data()`)
- `item_sales_parser.py` v2.0 - `11_Item_Sales_Weekly_Log_Star_Horse_Tracker.md` (Compact 4-section: Executive Summary + Scorecard + hidden JSON block + Flags & Actions. ~38% token reduction. JSON in `<!-- HERMES JSON BLOCK -->`. Per-store groups top-80%, top 5 food/drink, BCG, price/cost flags. Template block removed from file body.)
- `col_weekly_parser.py` v4.0 - `07_COL_Weekly_Log.md` (Compact 5-section format: Executive Summary + Scorecard + Daily Heatmap + Key Flags + JSON machine block. ~50% token reduction. 60/40 machine-human. No em dashes in output.)
- `cogs_parser.py` v3.4 - `03_COGS_Supplier_Monthly_Log.md` (rich format: full tables, flags, supplier summary, pricing actions)
- `menu_gp_parser.py` v2.0 - `14_Menu_GP_Monthly_Tracker.md` (multi-source: Star Horse + Recipe_Index + COGS Supplier Log; per-store accumulation schema; v2.0: 4-section format with hidden JSON block, Food/Bev Top10 & Bottom10 separate tables, `_classify()` with item_group + keyword fallback, per-store GP% estimation; COGS cost adjustment; MoM via split-on-month-header; accumulation auto-clean; v1.1→v2.0 migration: list→dict stores with integer distribution + `_est` flag)
- `wastage_parse_gen.py` v1.0 - `10_Wastage_WriteOff_Monthly_Log.md` + 2 HTML dashboards (COGS + Wastage)
  - GSheet Data tab → structured aggregation (by store, category, top items)
  - 11-section markdown entry (HERMES template) with Δ MoM
  - HTML dashboard generation (Chart.js, store filters, donut charts)
  - `--ingest` (full), `--report` (vault only), `--gen-html` (HTML only), `--verify`, `--month YYYY-MM`

### Weekly→Monthly Aggregation (Vault Markdown → Wiki Index)
- `monthly_cover_ingest.py` v0.2 - `Covers_Hourly_2026_Monthly_Index.md`
  - Weekly→monthly aggregation from vault markdown (no GSheet)
  - Deterministic (no LLM)
  - **5 data source types** in priority order: JSON block → Roll-up table → D1+split → D1 actual → Sum
  - Cross-month week proration (W14, W18) by day count
  - Delta report console output before write (Warren confirms)
  - `--month YYYY-MM`, `--dry-run`, `--force` flags
  - v0.2: Added JSON data block (v5.0) parser for `### 📊 Data` → `stores[i].c` extraction
  - v0.3: Code review findings applied — warn on JSON parse fail, key fallback 'c'→'covers', missing-store validation, removed dead code, simplified `determine_target_month`

## HERMES Template Block Convention (Vault-Wide)

Any periodic tracking file (weekly/monthly) with a structured format MUST have a **HERMES template block**... (existing content unchanged)

## HTML Dashboard Generation

Monthly operational parsers may optionally generate **interactive HTML dashboards** alongside markdown vault entries. These serve as visual decision-support for Warren, using Chart.js for interactive charts.

### Pattern

```python
# 1. Define HTML as a module-level constant string with {PLACEHOLDER} markers
_COGS_HTML = """<!DOCTYPE html>
<html>...{DATA_KPI}...{WO_ROWS}...</html>"""

# 2. Write a generator function that populates placeholders
def generate_cogs_dashboard(data: dict, month: str) -> str:
    import json
    kpi_data = {"ALL": {"rev": rev, ...}, "LU3": {...}}
    return _COGS_HTML.replace("{MONTH}", month) \
                     .replace("{DATA_KPI}", json.dumps(kpi_data)) \
                     .replace("{WO_ROWS}", json.dumps(wo_items))

# 3. Save to wiki directory
html_dir = VAULT_ROOT / "30_KNOWLEDGE_BASE" / "wiki" / "08_menu_cogs"
html_dir.mkdir(parents=True, exist_ok=True)
html_dir.write_text("COGS_Dashboard_2026-06.html")
```

### Dashboard Types

| Type | Charts | Used for | Example file |
|------|--------|----------|-------------|
| **GrabFood Trend Dashboard** | 6 charts: Orders, GMV, Net, Ad Spend, Commission %, Channel Mix. Multi-store + System dashed line. Green theme (`#CCFF99`/`#4CAF50`/`#1B5E20`/System=`#2196F3`). Data from `06_GrabFood_Weekly_Log.md` gf_data JSON blocks. | `GrabFood_Trend_Dashboard.html` (06_lusine_operations/) | `scripts/gen_grabfood_dashboard.py` |
| **COGS Dashboard** | Revenue vs COGS bar, Food vs Bev stacked bar, WO recon table, Top 25 items (3 tabs) | Warren opens in browser to browse monthly COGS metrics | `COGS_Dashboard_2026-06.html` (08_menu_cogs/) |
| **COL Trend Dashboard** | 3 charts: COL% trend (line, store series + System dashed), Pass Rate % (bar), SPLH Trend (line). Green theme: LU3 `#CCFF99`, LU5 `#4CAF50`, LU7 `#1B5E20`, System `#2196F3`, BG `#E8F5E9`. Threshold lines 15%/20%. Store filter tabs. Data from GSheet (07_COL_Weekly_Log tab). GSheets CSV export pattern, no PYTHONPATH needed. | Warren opens to see COL trajectory — system + per-store weekly trend | `COL_Trend_Dashboard.html` (04_labour_costs/) |
| **Wastage Dashboard** | WO/SH/Surplus stacked bar, Category donut, Action items panel, Top 10 WO + SH tables | Warren opens to assess write-off/shortage priorities | `Wastage_Dashboard_2026-06.html` |

### GrabFood Weekly Entry Format (v1.4+)

Each weekly entry now has this structure (after the `## {week_id} | {date_range}` header):

```markdown
## 2026-W27 | 29/06–05/07/2026

- **System:** 41 orders | Gross 14.5M | Net after ad 10.7M | ↑8% vs W-1
- **Ads active:** LU3 + LU5 — ROAS 10-20x
- **Cảnh báo:** Commission LU7 24.5% vượt ngưỡng 20%

📊 Channel Mix: LU3 4.2% | LU5 2.8% | LU7 0.1%
▶ REC: Continue ad LU3@484k — ROAS 13.9x | ...

### Revenue Summary (9 columns, no Comm%)
| Store | Orders | Gross GMV | Commission | Net Payout | Ad Spend | Net After Ad | Avg Order | vs W-1 |

### Daily Breakdown (7 days, 📢 = ad day, — = inactive)

🟡 LU3 19.6% | 🟡 LU5 19.6% | 🔴 LU7 24.5%

### MTD — Tháng MM/YYYY

<!-- gf_data: {expanded JSON with channel_mix, recommendation} -->
```

Key rules:
- **3-bullet Executive Summary** right under week header (System totals, Ad status, Flags)
- **No Flags section** — replaced by Commission line + Executive Summary
- **No Ad Spend or Delivery Reviews sections** — data preserved in JSON block
- **vs W-1** includes absolute delta: `↓31% (-3.1tr)`
- **LU7 = `—` when inactive** + `📌 LU7: inactive` note
- **JSON block expanded** with `channel_mix`, `recommendation`, `date_range`

### Central Dashboard Index (`00_DASHBOARDS.md`)

Place a `00_DASHBOARDS.md` file at `30_KNOWLEDGE_BASE/wiki/` as the centralized index for ALL HTML dashboards. Format:

```markdown
| Dashboard | File | Data Scope | Last Refresh | Nguồn Data |
|-----------|------|------------|-------------|------------|
| GrabFood Trend | [[06_lusine_operations/GrabFood_Trend_Dashboard.html]] | W18-W27 | 2026-07-06 | `06_GrabFood_Weekly_Log.md` |
| COGS Dashboard | [[08_menu_cogs/COGS_Dashboard_2026-06.html]] | Jun 2026 | ... | `03_COGS_Supplier_Monthly_Log.md` |
```

- **Physical files** live next to their data/analysis
- **Central index** links them all — one place to browse
- Each new dashboard adds 1 row to the index + 1 file to the wiki

### Key Design Rules

- **Static HTML only** — no server, no backend. Chart.js from CDN (`cdn.jsdelivr.net/npm/chart.js`).
- **Embed data as JSON** — `<script>var DATA = {JSON_STRING};</script>`, Chart.js reads from `DATA`.
- **Avoid f-string + JS `${}` conflict** — use `.replace()` on static template strings.
- **Store filter tabs** — "ALL / LU3 / LU5 / LU7" buttons toggle per-store view.
- **KPI cards** — 4-5 metric cards at top (Revenue, COGS%, WO, etc.).
- **Save to `30_KNOWLEDGE_BASE/wiki/08_menu_cogs/`** — alongside other COGS analysis files.
- **Update `00_WIKI_INDEX.md`** after creating new dashboard files.
- **CLI: `--gen-html`** flag to regenerate without touching vault.

### Reference Implementation
- `scripts/wastage_parse_gen.py` — `generate_cogs_dashboard()` + `generate_wastage_dashboard()`
- `30_KNOWLEDGE_BASE/wiki/08_menu_cogs/COGS_Dashboard_2026-06.html` — working output
- `30_KNOWLEDGE_BASE/wiki/08_menu_cogs/Wastage_Dashboard_2026-06.html` — working output

### Purpose
- Hermes reads this block before every edit/write → ensures consistent format
- New sessions know the rules without asking Warren
- Format rules survive context window resets

### Format
```html
<!--
╔══════════════════════════════════════════════════════════════════╗
║  🤖 HERMES TEMPLATE — BẮT BUỘC ĐỌC TRƯỚC KHI GHI FILE NÀY      ║
╠══════════════════════════════════════════════════════════════════╣
║  Mỗi [chu kỳ] mới phải có N SECTION (theo thứ tự):              ║
║                                                                  ║
║  1. ### Executive Summary — 3 BULLETS                           ║
║     - He thong: ...                                              ║
║     - Top/Bottom: ...                                           ║
║     - Key Takeaway: ...                                         ║
║                                                                  ║
║  [Các sections khác]                                             ║
║                                                                  ║
║  NGÔN NGỮ: Human content = TIẾNG VIỆT CÓ DẤU                    ║
║  Net Revenue = Gross * 0.882 (VAT 8%/10% + SC 5%)               ║
╚══════════════════════════════════════════════════════════════════╝
-->
```

### Placement
```
YAML frontmatter
---
[blank line]
<!-- HERMES TEMPLATE block -->
[blank line]
## 📋 Hướng dẫn sử dụng (optional — cho monthly logs)
  Các lệnh CLI, nguồn dữ liệu, file output — để Warren đọc là biết làm.
[blank line]
---
[blank line]
## YYYY-MM (newest entry on top)
...
```

### Usage Guide Convention
For **monthly operational logs**, add a `## 📋 Hướng dẫn sử dụng` section right after the HERMES template block, before the first data entry. This section tells Warren:
- **Steps** (e.g. "1. CFO gửi file → 2. Hermes chạy lệnh → 3. Kết quả")
- **CLI commands** (table: lệnh / chức năng)
- **Files generated** (vault entry + HTML dashboards)
- **Data source** (GSheet tab, revenue source)
- The section is informational only — Hermes follows the HERMES template block, not this guide, for format rules.

Reference: `10_Wastage_WriteOff_Monthly_Log.md` (COGS/Wastage monthly log).

### Enforcement
- Hermes MUST read this block before any edit/write to the file
- If a file has this block but Hermes skipped it → violation
- If a file doesn't have this block yet → Hermes proposes adding it on next edit
- The template block is WRITTEN BY HERMES — not manually maintained

### Reference Files
- `09_Hourly_Cover_Revenue_Log.md` — canonical example (4 sections, weekly)
- `10_Wastage_WriteOff_Monthly_Log.md` — second implementation (11 sections, monthly)

## Pending Parsers

- `google_review_parser.py` → `05_Google_Review_Weekly_Log.md`
- `payroll_cph.py` → `12_Wage_Structure_by_Role_Monthly.md`