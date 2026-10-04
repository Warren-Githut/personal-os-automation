# Menu GP% Parser — Cross-Sheet Join Pattern

**Script:** `vault/scripts/menu_gp_parser.py`
**Output:** `vault/10_OPERATION_DATA/14_Menu_GP_Monthly_Tracker.md`
**Created:** 2026-07-03

## What makes this different from other L'Usine parsers

Unlike most parsers (which ingest data from one GSheet tab → one log file), this parser **joins three data sources**:

| Source | What it provides |
|--------|-----------------|
| Star Horse GSheet (gid=72569880) | Per-SKU units sold + revenue per store (weekly) |
| Recipe_Index.json (109 recipes) | Standard recipe cost per menu item (baseline) |
| COGS Supplier Log (markdown) | Ingredient price changes for cost adjustment (TBD) |

## Cadence

- **Monthly** (not weekly — most other parsers are weekly)
- Manual trigger: `python3 vault/scripts/menu_gp_parser.py --month YYYY-MM`
- Calendar reminder: ngày 5 hàng tháng, 10:00
- Dry-run: `--dry-run` flag to preview without writing

## Key data flow

```
Star Horse GSheet ──┐
                    ├──> normalize item name → join → GP = rev - (qty × cost)
Recipe_Index.json ──┘
```

## Cross-check

Script cross-checks Star Horse total revenue vs `01_Weekly_Revenue_Log.md` for the same week (±4% threshold). Block entry if delta exceeds.

## Output format

6 sections per entry, prepended newest-on-top:
1. Tổng Quan — system-level GP%, top/bottom margin items
2. Flags — items below GP% target, recipe vs POS cost delta
3. Top 10 Best Margin — ranking by GP%
4. Bottom 10 Worst Margin — ranking by GP%
5. Items Without Recipe — unmatched items (extras, add-ons, bottled drinks)
6. (TBD) Menu Engineering Matrix — Star/PH/Dog/? quadrants

## Unmatched items (expected)

Items without recipe cards include:
- Bottled drinks (Acqua Panna, Coke, etc.)
- Cakes from Sharon supplier (outsourced)
- Set/combo menu variants
- New menu items (Avocado Toast 5.0 vs Recipe has 4.0)
- Extra/add-on items

These are explicitly listed in a "⚠️ Items Without Recipe" section.

## Future improvements

- COGS adjustment: integrate `cross_ref_cogs_recipe.py` logic to adjust recipe costs from supplier price changes
- Monthly accumulation: currently only latest week available in Star Horse GSheet
- Menu Engineering quadrants: Star/PH/Dog/? classification (parser has placeholder logic)
