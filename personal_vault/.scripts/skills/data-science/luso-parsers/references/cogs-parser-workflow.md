# COGS Parser — Full Workflow & Data Extraction

## Data Flow

```
Thao (Supply Chain) fills FM-PUR-06 Excel
        │
        ▼
Excel file sent to Warren (Desktop: FM-PUR-06 Price Change Approval rev00 - YYYY (Month).xlsx)
        │
        ▼
Data manually entered into GSheet tab "03_COGS_Supplier_Monthly_Log" (GID 865155568)
   (NOT "PRICE_CHANGE" — the tab name is the output log filename)
        │
        ▼
cogs_parser.py v3.4 reads GSheet via fetch_sheets_api() (Sheets API service account)
        │
        ▼
Writes to vault/10_OPERATION_DATA/03_COGS_Supplier_Monthly_Log.md
```

## GSheet Structure (GID 865155568)

The tab contains ALL months' price change rows combined, one row per item per month.

**Column mapping (verified 2026-06-30 via Sheets API):**

| GSheet Col | Data | Parser col index | Parser uses? |
|------------|------|-----------------|--------------|
| 0 | Row number | — | no |
| 1 | Items Descriptions | `get(1)` | ✅ item name |
| 2 | Supplier | `get(2)` | ✅ supplier |
| 3 | Unit | `get(3)` | ✅ unit |
| 4 | Last Price | `get(4)` | ✅ price_old |
| 5 | New Price | `get(5)` | ✅ price_new |
| 6 | % Change | `get(6)` | ✅ pct (strips `%` suffix, v3.3+) |
| 7–10 | Various (Note, Price, Buying info) | — | no |
| 11 | Qty buying (Volume) | `get(11)` | ✅ volume |
| 12 | Total buying (Impact) | — | no |

**Header detection:** `find_header_row()` scans rows 0–19 for a row containing both "item" and "supplier" label keywords.

**⚠️ Important:** GSheet Sheets API returns percentage values as **strings** like `"10%"`, not numbers. `to_float()` must strip `%` before `float()` conversion (v3.3+).

## Excel File Structure (FM-PUR-06)

The FM-PUR-06 workbook has separate tabs per month (Dec, Jan, Feb, ..., Nov, December).

**Tab structure (verified 2026-06-30):**

| Row | Content |
|-----|---------|
| 1 | "L Concepts (LC)" header |
| 2 | Form title + document code + Department: Procurement |
| 4 | "PRICE CHANGE APPROVAL" |
| 5 | Category checkboxes (F&B / Non food / Service / Capex) |
| 6 | Note with quantity buying period |
| 7 | Requested by, Approver info |
| 8 | Justification, Effective date (col D), Estimate impact (col M) |
| 9 | % impact, % total labels |
| 10 | **HEADER ROW**: No., Items Descriptions, Supplier, Unit, Last Price, New Price, %, Note, Price, BUYING FROM, PRICE, Qty buying, Total buying, % contribution |
| 11+ | Data rows |

## v3.4 Entry Format (7 Sections)

The parser now generates rich entries matching the manually-written June format. Each entry produces ~8,400 chars across 7 sections:

### Section 1: ⚡ Flags
- 🔴 items >13% needing pricing review (top 6 by %)
- ⚠️ no-volume items warning
- 💰 net COGS impact with direction

### Section 2: Tổng quan
```
**Tổng quan:** 77 items | 46 tăng giá | 23 giảm giá | 8 flat/không volume
**Net COGS impact: -1.929.158 đ**
```

### Section 3: Impact by Supplier
| Supplier | Items↑ | Items↓ | Net Δ VND/tháng | Avg %Δ |

### Section 4: Items Tăng Giá — Cần Chú Ý
Full 10-column table: # | Item | Supplier | Đơn vị | Giá cũ | Giá mới | Δ% | Volume/tháng | Impact | Flag

### Section 5: Items Giảm Giá — COGS Benefit
6-column savings table (≥100k threshold)

### Section 6: Menu Price Action Required
Items >13% with impact, decision status (⏳ Pending)

### Section 7: Actions
Review checklist + data request bullets

## Parser CLIs

```bash
# Default: current month
python3 cogs_parser.py

# Override any month
python3 cogs_parser.py --month 2026-07

# With env overrides (headless cron)
LUSINE_HEADLESS=1 LUSINE_FORCE=1 python3 cogs_parser.py
```

## Impact Calculation

```python
impact = pct / 100 * price_old * volume   # pct is in percent units (10 = 10%)
```

Note: The parser's impact may differ slightly from Excel's "Total buying" column (col M) due to rounding or formula differences.

## v3.4 Changes

| Change | Detail |
|--------|--------|
| `build_entry()` | Rewrote from 626-char summary to 8,437-char rich format with 7 sections matching June manual entry |
| `to_float()` | Strips `%` prefix for GSheet API compatibility |
| `--month` argument | `argparse` → `--month YYYY-MM` → `date(int(y), int(m), 1)` |
| `month_header` | Changed from `%m/%Y` to `%Y-%m` — must match `build_entry()` format |
| Duplicate functions | Removed redundant `aggregate_changes()`, `fmt_vnd()`, `flag_emoji()` from bottom of file |
| `calc_impact()` | Extracted as standalone helper |
| `defaultdict` | Added for supplier aggregation |
| `fmt_vnd(0)` | Returns `"—"` instead of `"0 đ"` |

## Known Issues

1. **Double `vault/` path:** `VAULT_ROOT = Path(__file__).parent.parent.parent.parent` resolves to `Warren_OS_Local/`, then `VAULT_ROOT / "vault" / "10_OPERATION_DATA"` — correct only if the parser lives at `../vault/10_OPERATION_DATA/parsers/cogs_parser.py`. Fragile if moved.
2. **GID mismatch in frontmatter:** The log frontmatter says `sheet_name: PRICE_CHANGE` but the actual tab name is `03_COGS_Supplier_Monthly_Log`. Cosmetic — the GID is correct.
3. **No month-scoped filtering:** All months' data lives in one flat table. The parser writes ALL rows without filtering by month. Dedup relies on checking `## YYYY-MM` header existence in the log.
4. **Comma-sensitive price parsing:** `to_float()` uses `.replace(",", "")` for price strings. If the format changes (spaces, dots as thousands separators), parsing breaks silently.
