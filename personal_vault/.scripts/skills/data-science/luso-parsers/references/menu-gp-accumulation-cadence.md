# Menu GP Accumulation — Cadence & Repair Recipe (session 2026-08-03)

Supporting detail for the `luso-parsers` SKILL.md "Menu GP Monthly — Accumulation Cadence..." subsection.

## Evidence: Star Horse sheet keeps only the current week
- 21 columns total; exactly 1 week-column: `history_11_Item_Sales_Weekly_Log_Star_Horse Restaurant name: L-Concepts Period: from 7/6/2026 to 7/12/2026` (→ W28).
- Grep for `7/13|7/20|7/27|8/2/2026` across all column names → 0 hits.
- Therefore: no backfill possible from sheet after a week rolls off. Weekly `--accumulate` is the ONLY capture path.

## W28 format-rot (before repair)
`item_sales.json["2026-W28"]` (note old key prefix) =
```json
{ "week_start":"2026-07-06",
  "stores": { "LU3":{qty,rev,avg_price}, "LU5":{...}, "LU7":{...}, "System":{...} } }
```
← NO `"items"` key.
→ `load_accumulated_month("2026-07")` → iterates `wdata.get("items", {})` → empty → dry-run: `Accumulated: 1 weeks, 0 unique items` → parser exits, no write.

## After re-accumulate (sheet still on W28)
`item_sales.json["W28"]` (new key, no prefix) =
```json
{ "week_start":"2026-07-06",
  "items": { "avocado toast 4.0":{item_name,item_group,qty,net_rev,stores}, ... 158 keys } }
```
→ dry-run: `Accumulated: 1 weeks, 158 unique items`; `_metadata.months` gains `"2026-07"`.

## Commands (copy)
Read-only probe (no vault write):
```bash
cd C:/Users/khoans/Documents/Warren_OS_Local/vault/scripts
python3 -c "from menu_gp_parser import fetch_star_horse, detect_week_id; parsed, cols = fetch_star_horse(); wid, ws = detect_week_id(cols); print('WEEK:', wid, ws, '| items:', len(parsed)); import re; print('future-week cols:', [c for c in cols if re.search(r'(7/13|7/20|7/27|8/2)/2026', str(c))])"
```
Repair accumulate (only while sheet is on that week):
```bash
cd /c/Users/khoans/Documents/Warren_OS_Local && python3 vault/scripts/menu_gp_parser.py --accumulate
```
Monthly parse + dashboard:
```bash
cd /c/Users/khoans/Documents/Warren_OS_Local
python3 vault/scripts/menu_gp_parser.py --month 2026-07 --dry-run
python3 vault/scripts/menu_gp_parser.py --month 2026-07
python3 vault/scripts/gen_menu_gp_dashboard.py
```

## Cadence reminder (system lesson)
Monthly GP = snapshot taken the 1st Monday of the FOLLOWING month. By then the sheet shows next month's week, so all 5 prior weeks must already be in `item_sales.json`. Miss one weekly `--accumulate` → that month is permanently incomplete. Warren runs these manually (no cron) via pasteable blocks — see SKILL.md body.
