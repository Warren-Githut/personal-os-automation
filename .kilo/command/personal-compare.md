---

description: "Cross-store comparison (LU3/LU5/LU7) — 1 metric, multiple stores, instant table. Adapted for ORION+Deepseek toolchain."
updated: 2026-06-02
---

# /ops-compare — Cross-Store Comparison
# v1.0 | 2026-05-27
# ORION+Deepseek adaptation: read_file (data source), search_files (find latest), execute_command (CSV parse)
# PURPOSE: Compare 1 metric across LU3/LU5/LU7 without hopping between 3 files.
# OUTPUT: Temporary analysis only. Never auto-writes to wiki. Warren decides via /ops-ingest.

---

## USAGE

```
/ops-compare [metric] [period] [store?]
```

### Examples

| Command | What it does |
|---------|-------------|
| `/ops-compare revenue w22` | Revenue W22: LU3 vs LU5 vs LU7 |
| `/ops-compare col apr` | COL% April: all stores |
| `/ops-compare cph 2026-04` | CPH by role: all stores |
| `/ops-compare covers apr` | Avg covers/hour April: all stores |
| `/ops-compare rating may` | Google rating latest: all stores |
| `/ops-compare grabfood w22 lu3,lu5` | GrabFood W22: LU3 + LU5 only |
| `/ops-compare cogs apr` | COGS% April: all stores |
| `/ops-compare hr apr` | Headcount April: all stores |

### Supported Metrics

| Metric | Source file(s) | Stores |
|--------|---------------|--------|
| `revenue` / `rev` | `10_OPERATION_DATA/01_Weekly_Revenue_Log.md` | LU3, LU5, LU7 |
| `col` | `10_OPERATION_DATA/07_COL_Weekly_Log.md` | LU3, LU5, LU7 |
| `cph` | `30_KNOWLEDGE_BASE/raw/cph_result_*.csv` | LU3, LU5, LU7 |
| `covers` | `30_KNOWLEDGE_BASE/wiki/labour_costs/Covers_Hourly_*` | LU3, LU5, LU7 |
| `rating` / `reviews` | `10_OPERATION_DATA/05_Google_Review_Weekly_Log.md` | LU3, LU5, LU7 |
| `grabfood` / `gf` | `10_OPERATION_DATA/06_GrabFood_Weekly_Log.md` | LU3, LU5 (LU7 not launched yet) |
| `lto` | `10_OPERATION_DATA/04_LTO_Weekly_Log.md` + wiki/lto_tracker/ | Per-store |
| `cogs` | `10_OPERATION_DATA/03_COGS_Supplier_Monthly_Log.md` | LU3, LU5, LU7 |
| `hr` | `10_OPERATION_DATA/02_HR_Weekly_Log.md` | LU3, LU5, LU7 |
| `pl` / `p&l` | `30_KNOWLEDGE_BASE/wiki/P&L_Budget/` | LU3, LU5, LU7 |

---

## PROTOCOL

### Step 0 — Parse args

Extract from user input:
- **metric** → map to source file (see table above)
- **period** → normalize to: `YYYY-WXX`, `YYYY-MM`, or `YYYY-QX`
- **stores** (optional) → default all stores in source; accept `lu3`, `lu5`, `lu7` filter

Normalization rules:
| Input | Normalized | Example file section |
|-------|-----------|---------------------|
| `w22`, `W22`, `week22` | `2026-W22` | `## 2026-W22` in log files |
| `apr`, `april`, `04` | `2026-04` | `202604` in CSV filenames |
| `may`, `05` | `2026-05` | — |
| `q1`, `q2` | `2026-Q1`, `2026-Q2` | wiki quarterly files |
| `2026-04` (explicit) | `2026-04` | as given |

If period can't be parsed → ask Warren to clarify.

### Step 1 — Read data

**For operational logs** (revenue, col, reviews, grabfood, hr):
1. `read_file(path="10_OPERATION_DATA/{source}")` — read full file
2. `search_files(regex="^## {normalized_period}", file_pattern="{source}", path="10_OPERATION_DATA")` — find exact section
3. Extract table rows — parse markdown table by store column

**For wiki files** (covers, pl):
1. `search_files(regex="{normalized_period}", file_pattern="*.md", path="30_KNOWLEDGE_BASE/wiki/labour_costs/")`
2. Read matched sections

**For raw CSVs** (cph):
1. `read_file(path="30_KNOWLEDGE_BASE/raw/cph_result_{normalized_period}.csv")`
2. Parse rows by store

### Step 2 — Build comparison table

Render compact table with store columns side-by-side.

**Table template:**

```
## 📊 {Metric} — {Period}

| Store | {Column A} | {Column B} | {Column C} | Flag |
|-------|-----------|-----------|-----------|------|
| LU3   | X         | X         | X         | ✅/🟡/🔴 |
| LU5   | X         | X         | X         | ✅/🟡/🔴 |
| LU7   | X         | X         | X         | ✅/🟡/🔴 |
```

**Red flag rules per metric (copy from each log file's header):**
- **revenue:** any store W/W < -15% → 🔴
- **col:** any store COL% >20% → 🔴; 15-20% → 🟡
- **rating:** any store <4.3 → 🔴
- **grabfood:** delivery rating <4.0; commission >20% gross; Ad ROAS <1x → 🔴
- **cph:** above/below benchmark range → flag per segment

### Step 3 — Insight + analysis

Add 2-3 bullet insights below table:
- Biggest variance driver
- Week-over-week / month-over-month trend
- Cross-store pattern (e.g., "LU5 consistently lowest COL%")

### Step 4 — Recommend + Ask Warren (per CLAUDE.md §3C)

**Mandatory: ORION self-recommends A/B/C with reasoning first, then Warren decides.**

```
📊 **{Metric} comparison — {Period}** done.
⏱️ Would take ~X min manually (3 file hops) → /ops-compare done in 1 command.

⭐ Importance: [HIGH/MOD/LOW] — [short reason]
🎯 Actionable: [yes/no + what]

👉 I recommend: [A/B/C]
Reason: [based on insight importance + complexity + cost tradeoff — brief, convincing]

Warren decides:
[A] /ops-ingest with deepseek-reasoner (standard) — simple insight, 1 metric, cost ~$0.02-0.05
[B] /ops-ingest with deepseek-reasoner (deep) — cross-reference multi-metric, strategic decision
[C] Skip — temporary analysis, do not save to wiki
```

- **Wait for Warren's choice.** Do not auto-execute anything after recommending.
- If Warren chooses [A] or [B] → run `/ops-ingest` protocol
- If [C] → analysis lives in conversation context only, done

---

## ANTI-PATTERNS

- **No auto-write** — /ops-compare never auto-writes to wiki. Always ask.
- **No bad period parsing** — if section not found → tell Warren, do not invent data.
- **No comparing incompatible data** — e.g. LU7 has no GrabFood yet → write "N/A (not launched yet)".
- **No file writes** — surgical edits only. /ops-compare is read-only analysis.

---

## SCOPE

- **Temporary analysis only** — data lives in conversation context.
- **No wiki writes** — unless Warren says yes → use `/ops-ingest` protocol.
- **No file mutations** — read-only across all data sources.
- **No log entries** — no need to log in ACTIVITY_LOG.md since no files created/modified.
