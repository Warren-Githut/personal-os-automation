---
name: lusine-recipe-cogs
type: skill
domain: lusine_operations
status: active
version: 2026-07-16
description: Maintain L'Usine Recipe_Index.json (IKKO POS cache) and compute combo GP matrices for promo planning. Covers ingesting recipe CSV/XLSX from Warren, adding to JSON without dup, verifying cost integrity, and building price-combo GP tables. Embeds Warren's hard rule - NEVER estimate cost, ask if missing.
---

# lusine-recipe-cogs

Manage the L'Usine menu COGS cache (`vault/30_KNOWLEDGE_BASE/wiki/08_menu_cogs/Recipe_Index.json`) and compute Gross Profit (GP percent) for combo pricing decisions.

## When to use
- Warren sends a recipe CSV or XLSX (cost card from kitchen) to add to Recipe_Index.json
- Planning a price combo (e.g. "169k combo = 1 main + 1 drink") and need GP matrix
- Checking menu coverage: which main-menu items are missing from Recipe_Index
- Any COGS or GP percent question for L'Usine promos

## Hard rules (Warren, 2026-07-16)
1. NO ESTIMATION. If a cost is missing from data, STOP and ask Warren to supply the CSV/XLSX. Never guess cost_total, never interpolate from similar items. Quote from session: "lam viec voi tao la ko co uoc luong, ko biet thi phai keu tao cung cap".
2. VERIFY before claiming done. After editing JSON, run an independent Python recompute (sum ingredients vs cost_total, no dup item_name, GP bounds). Ad-hoc script in Temp with hermes-verify- prefix, then delete.
3. CONVERSION HOOK over post-purchase upsell. When planning a promo for pass-by traffic, the hook (price or value) must sit ON the standee or menu BEFORE the customer enters, not revealed after they sit down. Warren rejected post-purchase "you get 10 percent off or free kem" framing as ineffective for converting mall walkers.

## Recipe_Index.json structure
Each recipe = item_name, price_vnd, cost_total, cogs_pct, ingredient_count, ingredients list of type/name/uom/qty/cost_vnd, _source_file.
- cost_total = sum of ingredient cost_vnd (VND, NOT thousands)
- cogs_pct = cost_total divided by price_vnd times 100
- Source CSV/XLSX from IKKO POS export: the "Cost, VND" row is in thousands (e.g. "53.01" means 53,010 VND). Multiply by 1000.
- File is at vault/30_KNOWLEDGE_BASE/wiki/08_menu_cogs/Recipe_Index.json (NOT raw/ because raw is READ-ONLY).

## Ingest workflow (CSV or XLSX)
1. Read attachment. CSV: cat via terminal. XLSX: openpyxl and pandas are BROKEN on hermes venv (Python 3.14, numpy C-extension mismatch; openpyxl style error applyFormat). Use raw XML parse, see references/xlsx_raw_xml_parse.md.
2. Extract: item_name, price (VAT inclusive), cost_total (times 1000 from Cost VND row), ingredients list.
3. Check if item_name already exists, skip if dup and warn Warren.
4. Append recipe block to end of recipes array (before closing bracket). Keep cogs_pct accurate.
5. Run verify script (see below).

## Combo GP matrix
Given combo price P, foods with cost, drinks with cost:
    gp percent = (P - food_cost - drink_cost) / P * 100
- Report min and max GP across all food times drink cells.
- Flag any cell under 50 percent (too thin) or under 55 percent (review). For dead-hour promos, Warren accepts GP around 50 percent because fixed costs run idle.
- Example: 169k combo, Carbonara (47.4k) + Watermelon Juice (6.5k) = 68.1 percent GP; Chicken Burger (58.7k) + Pandan Coconut (18.4k) = 54.4 percent GP.

## Verify script template (ad-hoc)
See scripts/verify_recipe.py. Loads JSON, asserts no dup, asserts cost_total equals sum of ingredients, prints combo GP matrix. Run from Temp, delete after.

## search_files caveat (Windows git-bash)
search_files with target files frequently FAILS to find files under vault (path resolution bug). If a file exists but search returns 0, use read_file with full absolute path directly. This bit Warren twice (hourly log, Recipe_Index.json).

## Source files
- Recipe_Index.json: vault/30_KNOWLEDGE_BASE/wiki/08_menu_cogs/Recipe_Index.json
- Menu PDF: liteparse first, then extract items (see verify-parser-output gate)
- Hourly covers: vault/10_OPERATION_DATA/09_Hourly_Cover_Revenue_Log.md (W28 LU5: 8-10h=176 cov/57.2M, 18-21h=78 cov/15.1M)
