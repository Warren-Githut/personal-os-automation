# Monthly Cover Aggregation — Session Detail

> Support file for `lusine-parser-standardization` skill, section *Weekly-to-Monthly Aggregation Pattern*.
> Created: 2026-07-03 during Monthly Cover ingest interview. Updated: 2026-07-03.

## Data Source Anatomy

Source: `10_OPERATION_DATA/09_Hourly_Cover_Revenue_Log.md`

### Weekly Section Structure (v5.0+)

```
## 2026-W<number> | <date_range>

### 📊 Data                                           ← v5.0 PRIMARY: compact JSON block
```json
{"week_id":"2026-W26","stores":[{"id":"LU3","c":836},{"id":"LU5","c":778},{"id":"LU7","c":773}]}
```

### Executive Summary                              ← summary, not raw data
### 🔥 Decision Board                              ← decision flags
### Hourly Detail -- <Store>                        ← hourly tables (3 stores, no ALL table)

### Weekly Roll-up (Δ vs W<prev>)                   ← fallback for older weeks (W24+)
| Store | Actual Covers | Gross Covers | Split | Net Revenue | Rev/Cover |

### <Store> -- Hourly Covers . Net Revenue (k)     ← D1 fallback for older weeks (< W24)
| **D1** | **day1** | ... | **week_total** |

### ALL -- Hourly Covers . Net Revenue (k)         ← SYSTEM peak hour section
### MTD - Tháng X/YYYY                              ← ROLLING, NOT reliable for monthly
### 📈 Dashboard                                     ← link to dashboard.html
```

### Date Range Format (3 variants)

| Format | Example | Parser |
|--------|---------|--------|
| ISO arrow | `2026-06-01 -> 2026-06-07` | Split on `->`, trim |
| DD/MM em-dash | `22/06–28/06/2026` | Split on `–` (U+2013), parse DD/MM/YYYY |
| Single (rare) | `2026-04-06` | Treat as start of 7-day week: `end = start + 6d` |

### Weekly Roll-up Availability

| Week range | Roll-up present? | Notes |
|------------|-----------------|-------|
| W24+ (2026-06-08 onward) | ✅ Yes | Standard format |
| W23 (2026-06-01 to 2026-06-07) | ❌ No | Must use D1 fallback |
| W14-W22 (March-May) | ❌ No | Must use D1 fallback |

### D1 Row Extraction

From each `### <Store> -- Hourly Covers` section:
```python
# Pattern: | **D1** | **day1** | ... | **week_total** |
# D1 row is last row before next section header or blank line
# Wk Sum is last bold number in row
# Returns: per-store weekly actual covers
```

## D1 Format Variants (CRITICAL)

The D1 row label and semantics vary by week. There are 4 formats:

| Format | Weeks | Label | Split orders | Formula |
|--------|-------|-------|-------------|---------|
| **A — Old D1+Split** | W14-W18 | `**D1**` | `*Split orders: +XXX*` comment in D1 row | actual = D1_cover + split_order_count |
| **B — D1 Actual** | W19 | `**D1**` | No split comment. Header says "Split bill excluded" | D1 IS actual covers |
| **C — Sum Actual** | W20 | `**Sum**` | No split comment. Header references split accounting | Sum IS actual covers |
| **D — Roll-up Primary** | W24+ | `**D1**` | Roll-up table is primary source; D1 row ignored | Use roll-up Actual Covers column |

**Detection heuristics in order:**
1. If section has `### Weekly Roll-up` table → use roll-up (format D)
2. Else try `**D1**` row → check for split orders comment → if found, add to D1 (format A)
3. Else try `**D1**` with no split comment → use as-is (format B)
4. Else try `**Sum**` row → use as-is (format C)

**BUG TO AVOID:** The `### ALL -- System Summary` section also has a D1 row. If the parser doesn't clear `current_store` when entering non-store sections (ALL, Conversion), ALL's D1 gets attributed to LU7. Reset `current_store = None` on any `###` header that isn't LU3/LU5/LU7.

**W21 edge case:** Source file may have truncated week sections (incomplete `|---|---` row with no data below). The D1 parser will skip weeks with no data row. This means ~1 week of May data is missing (~2,500 covers). Document in the Notes column of the monthly index.

## 12h Peak Hour Extraction

From `### ALL -- Hourly Covers` section:
```python
# Pattern: | 12 | mon_covers . mon_rev | ... | **week_total_covers . week_total_rev** |
# week_total_covers = sum of 12h covers across all days in that store
# System 12h = sum of LU3 + LU5 + LU7 12h
```

**Split issue**: The `| 12 |` row values are `covers . revenue_k` separated by ` . ` (space-dot-space). Extract covers before the dot.

## Monthly Aggregation Logic

### Week-to-Month Boundary

A week's date range determines month membership:

| Week | Dates | Month assignment |
|------|-------|-----------------|
| W18 | 2026-04-27 → 2026-05-03 | ⚠️ **SPLIT** — 4 days Apr, 3 days May |
| W14 | 2026-03-30 → 2026-04-05 | ⚠️ **SPLIT** — 2 days Mar, 5 days Apr |

**Approach (session decision): Prorated by day count.**
- Only 2 weeks cross months. Compute daily avg × days-per-month.
- Formula: `month_portion = week_total * days_in_this_month // total_week_days`
- Acceptable approximation — difference is <2% for any month.

### Output: 5 Sections

### Section 0: Executive Summary

```
| Metric | Apr | May | Jun | **Q2** | **YTD** |
|--------|-----|-----|-----|--------|---------|
```

### Section 1: System Cover Summary

```
| Month | LU3 | LU5 | LU7 | **System** | Δ MoM | Notes |
```
- **CRITICAL — Δ MoM baseline:** Use the FILE's previous month data (authoritative), not the computed value. When they diverge (e.g. file says Apr=13,455, computed says 11,803), the Δ must be relative to the file's number. Document discrepancy.

### Section 2: Average Covers per Day

```
| Month | LU3 | LU5 | LU7 | System | Days |
```

### Section 3: System Peak Hour (12h)

```
| Month | LU3 12h | LU5 12h | LU7 12h | **System 12h** | % of Daily Total |
```

### Section 4: Revenue per Cover (k VND)

```
| Month | LU3 | LU5 | LU7 | **System** |
```

## Common Bugs & Fixes (from monthly_cover_ingest.py v0.1)

| Bug | Root Cause | Fix | Severity |
|-----|-----------|-----|----------|
| **ALL section D1 attributed to LU7** | `current_store` not reset on non-store `###` headers | `if line.startswith('### ') and not sm: current_store = None` | 🔴 |
| **Duplicate separator lines in cover table** | State-machine in `write_index`: writes new separator then passes original separator through `else: output.append(line)` | Skip `|---|---` lines after `cover_table_written = True` | 🔴 |
| **YTD row overwritten with dashes** | YTD row hardcoded as placeholder | Preserve existing YTD row from original file | 🔴 |
| **Avg table loses existing rows** | Skip logic removes ALL existing month rows (Jan-Jun) | Only replace rows that have new computed data; keep rest | 🔴 |
| **Jun written even with `--month 2026-05`** | `--month` flag didn't filter write function | Pass `target_month` to `write_index()` and filter in both month_rows + avg_rows loops | 🟠 |
| **Δ MoM May vs Apr = -14.2% instead of -24.7%** | Computed using script's Apr (11,803) not file's Apr (13,455) | Manual override during review. Script should read file's prev month for Δ baseline | 🟠 |

## Verification Patterns (used in this session)

**Incremental ad-hoc testing (each slice):**
```python
# Write temp script → run → rm. Keep pattern:
# 1. Test week header parsing (all 3 date formats)
# 2. Test roll-up extraction (W24+ known values: LU3=836, LU5=778, LU7=773)
# 3. Test D1 fallback (W23 no roll-up, W14 cross-month)
# 4. Test ALL-section D1 exclusion (W23 LU7 < 2000, not 2952)
# 5. Test monthly aggregation (Apr exists, system > 10000)
# 6. Test existing index reading (Apr system=13455)
# 7. Test file write integrity (no duplicates, correct order)
```

**E2E final gate:**
```bash
python3 vault/scripts/monthly_cover_ingest.py --dry-run  # check delta
python3 vault/scripts/monthly_cover_ingest.py --month YYYY-MM  # real write
git diff vault/30_KNOWLEDGE_BASE/wiki/04_labour_costs/Covers_Hourly_2026_Monthly_Index.md  # verify
```

**Key test assertions (spot-check before each deployment):**
- JSON W26: LU3=836, LU5=778, LU7=773 (v5.0 JSON block)
- JSON W27: LU3=762, LU5=750, LU7=714 (v5.0 JSON block)
- Roll-up W26: LU3=836, LU5=778, LU7=773 (known values from GSheet)
- D1 W23 LU7 < 2000 (not contaminated by ALL section)
- W14 cross-month: Mar (2d), Apr (5d)
- No JSON/roll-up/D1 data for a week → skip (not crash)
- Apr existing: system=13,455 (file authoritative)

## Known Data Issues

| Issue | Impact | Status |
|-------|--------|--------|
| **Existing Apr (13,455) ≠ computed Apr (11,803)** | Existing from CSV export; weekly log uses D1 format | Skip Apr unless `--force` |
| **W21 source data truncated** (incomplete `|---|---`) | May missing ~2,500 covers | Note in May's Notes column |
| **Δ MoM May vs Apr uses file's 13,455 not computed 11,803** | May Δ = -24.7% not -14.2% | Manual entry during review |

## May 2026 Import Results

```
LU3:  3,220  (from W18[3d]+W19+W20+W22, W21 missing)
LU5:  3,472  (from W18[3d]+W19+W20+W22, W21 missing)
LU7:  3,434  (from W18[3d]+W19+W20+W22, W21 missing)
System: 10,126
Δ MoM: -24.7% (vs Apr 13,455)
YTD: 65,672 (adds Jan-May: 14,615+12,824+14,652+13,455+10,126)
```

## June 2026 Import Results (v0.2 — first JSON block ingest)

```
LU3:  3,676  (from W23+W24+W25+W26+W27[2d])
LU5:  3,452  (from W23+W24+W25+W26+W27[2d])
LU7:  3,506  (from W23+W24+W25+W26+W27[2d])
System: 10,634
Δ MoM: +5.0% (vs May 10,126)
YTD: 76,306 (adds Jan-Jun)
```

**Data sources for June:**
- W23-W25: Restored from `dashboard.html` WEEKS array (Revenue Log / PowerBI data)
- W26-W27: Parsed from v5.0 JSON block (GSheet data)
- **⚠️ Source discrepancy:** dashboard numbers differ ~1% from GSheet JSON (W26: 2,370 vs 2,387). Mixed-source 10,634 is approximate ±20-30 covers.

## `parse_json_block()` Pattern

Added in v0.2 to handle v5.0 compact JSON format (`### 📊 Data` + `` ```json `` block).

### Key details:
- Looks for ````json` opening and closing ```` fences within a week section
- Extracts `stores[i].c` as actual covers per store
- Returns empty dict if no JSON block, parse fails, or no valid stores
- Only accepts LU3/LU5/LU7 store IDs

### Implementation (extract_covers priority chain):

```python
def extract_covers(section):
    # Priority 1: JSON data block (v5.0 format)
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

### Verification tests (ad-hoc script, 6 tests):

```python
# Test 1: W26 JSON — LU3=836, LU5=778, LU7=773
# Test 2: W27 JSON — LU3=762, LU5=750, LU7=714
# Test 3: No stores field → empty dict
# Test 4: Malformed JSON → empty dict
# Test 5: No JSON block at all → empty dict
# Test 6: extract_covers integration → same as Test 1
```

## Data Restoration from Dashboard HTML

When compressed week sections (`<!-- ⏤ Compressed — data archived in dashboard HTML -->`) lack parseable data, restore from `30_KNOWLEDGE_BASE/wiki/09_hourly_cover_revenue/dashboard.html`.

### Data location

The dashboard embeds a `WEEKS` JS array (single line ~ line 125):
```javascript
var WEEKS = [{"label": "W23", "stores": {"LU3": {"covers": 968}, "LU5": {"covers": 755}, "LU7": {"covers": 835}}, "sys": {"covers": 2558}}, ...];
```

### Process

1. Extract WEEKS array from dashboard HTML
2. For each compressed week, extract `stores[Store].covers`
3. Inject as a JSON data block into the weekly log:
   ```json
   {"week_id":"2026-W23","period":"01/06-07/06/2026","stores":[{"id":"LU3","c":968},{"id":"LU5","c":755},{"id":"LU7","c":835}]}
   ```
4. Re-run `monthly_cover_ingest.py` — parser picks up restored data

### Compressed weeks identified (June 2026)
- W23 (01-07 Jun), W24 (08-14 Jun), W25 (15-21 Jun) — all compressed as JSON-only entries without machine-readable data blocks. Data restored from dashboard.

### ⚠️ Source inconsistency
W26 and W27 have BOTH dashboard data and GSheet JSON data. The diff is ~1%:

| Week | Store | Dashboard | JSON (GSheet) | Diff |
|------|-------|-----------|---------------|------|
| W26 | LU3 | 827 | 836 | +9 |
| W26 | LU5 | 770 | 778 | +8 |
| W26 | LU7 | 773 | 773 | 0 |
| W27 | LU3 | 756 | 762 | +6 |
| W27 | LU5 | 746 | 750 | +4 |
| W27 | LU7 | 714 | 714 | 0 |

Root cause: different split-orders treatment (Revenue Log vs GSheet). Acceptable for monthly aggregation. Document in Notes.

## Frontmatter Enrichment Pattern

The monthly index file now has **23 YAML frontmatter fields** for grep-ability:

```yaml
name, domain, type, status, owner, author, created, last_updated,
schema_version, stores, cadence, trigger, data_source, parser,
coverage, metrics, key_definitions, targets, tags, aliases,
related, see_also, update_history
```

Key additions that made the biggest difference for search:
- `aliases` — alternative names for the entity, grep-able
- `update_history` — chronological log of what changed when
- `metrics` — what this file tracks (useful for LLM routing)
- `coverage` — date range the data covers

## Template Locations

- Script: `vault/scripts/monthly_cover_ingest.py`
- Output index: `30_KNOWLEDGE_BASE/wiki/04_labour_costs/Covers_Hourly_2026_Monthly_Index.md`
- Weekly log: `10_OPERATION_DATA/09_Hourly_Cover_Revenue_Log.md`

## Google Calendar: Schedule

- Recurring: 5th of each month at 10:00
- Calendar ID: nguyen.s.khoa@gmail.com
