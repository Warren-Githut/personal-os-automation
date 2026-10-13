---
name: purchasing-dashboard
description: >
  Builds an interactive HTML "Purchasing Dashboard" for L-Concepts restaurant group
  (LU3, LU5, LU7) from monthly "Purchases report by goods and suppliers" Excel exports.
  Trigger whenever the user says "purchasing dashboard", "combine purchasing", "update
  purchasing", "run purchasing dashboard", "chạy purchasing dashboard", "phân tích giá
  mua hàng", "biến động giá nguyên liệu", or drops new monthly purchasing .xlsx files
  into the Purchasing/Data folder and asks to build, update, or refresh the report —
  even if they don't say the word "dashboard". Reads every monthly file, filters to
  external-supplier purchase invoices only (excludes internal inter-location transfers
  and the closed LU4 central kitchen), aggregates monthly spend per location and
  category, and runs price-change analyses: this-month dollar-impact movers (both
  item-level and rolled up by category), category Laspeyres price index, supplier
  price creep, and top % movers — plus a filterable/sortable item-by-item price detail
  table with red/green price-move highlighting, and a store-selectable item volume/spend
  table (toggle between quantity purchased and $ amount, per location). Always use this
  skill — do not rebuild the pipeline by hand, the filtering and price-change math have
  non-obvious correctness traps (see below).
---

# Purchasing Dashboard — L-Concepts

Turns the monthly "Purchases report by goods and suppliers" exports (one .xlsx per
month) into a single self-contained HTML dashboard: monthly spend per location and
category, plus complementary views of *why* prices moved and *how much* of each item
each store actually bought. Read this whole file before running anything — the
filtering and price-change methodology below fix real bugs found through user
feedback, and skipping them silently reintroduces double-counted spend or misleading
"price increase" labels.

## Settings

```python
DATA_FOLDER = r"C:\Users\Pham Thi Kim Loan\Desktop\Claude\Purchasing\Data"
OUTPUT_FILE = r"C:\Users\Pham Thi Kim Loan\Desktop\Claude\Purchasing\Purchasing_Dashboard.html"
```

Each new month drops in as `YYYY.MM.xlsx` (e.g. `2026.08.xlsx`) inside `DATA_FOLDER`.
The pipeline re-reads **every** file in the folder each run and rebuilds the dashboard
from scratch — there's no incremental state, so it's always consistent even if old
months get corrected or a file is dropped in out of order.

## Source file format

Each monthly file has one sheet (name may vary slightly — always use
`wb.sheetnames[0]`, don't hardcode the sheet name). Row 3 (1-indexed) is the header;
data starts row 4. The columns that matter (0-indexed after `iter_rows`):

| idx | Column | Notes |
|---|---|---|
| 0 | Accounting day | date |
| 1 | Document number | prefix (`LU3-…`, `LU4-…`, `LU5-…`, `LU7-…`) gives the location |
| 3 | Operation type | `"Purchase invoice"` = real purchase row; `"Expenditure invoice"` = internal consumption/transfer, not purchasing — always exclude |
| 4 | SKU | |
| 5 | Product | display name |
| 6 | Product qty | |
| 7 | Average price | per-unit price for that line |
| 12 | Product group | this is the usable **category** field (Fruit, Vegetable, Meat, Egg & Dairy, Dry Store, Beverage, Seafood, Cold Cut, …). Column 11 ("Product category") is almost always empty — don't use it. |
| 17 | Contractor | supplier name, OR an internal transfer marker (see below) |
| 25 | Storage | e.g. `LU3-KIT`, `LU5-BAR` — sub-location detail, not used in this dashboard (per user preference, keep to location-level only) |
| 27 | Amount | the spend figure to use. Verified identical to "Amount excluding VAT" (col 14) in every row of this dataset — VAT is not broken out here, so either column works, but use `Amount` for consistency. Also verified `qty × price == Amount` for every row. |

## Step 1 — Read and filter

Two non-obvious filters matter here, both discovered by checking the data rather than
trusting column labels at face value:

**1. Location scope: LU3, LU5, LU7 only.** LU4 was a central kitchen / commissary
(storage code `LU4-CENTRAL_KIT`), not a customer-facing store. It closed permanently
in March 2026 (confirmed by the user) — its purchase data drops to near-zero after
that month. Exclude it entirely; don't show it as a location trending to zero.

**2. External suppliers only — exclude internal transfers.** Some rows tagged
`"Purchase invoice"` are not real external purchases: their Contractor field is an
internal transfer marker like `"LU3-LTT-Q1: LU3-BAR"` or `"LU4-TD-Q2: LU4-CENTRAL_KIT"`
(document number also contains `"-INT-"`). These represent stock moving between
locations, not money paid to a vendor. If you sum every `"Purchase invoice"` row at
face value, group-wide spend gets double-counted: once when the origin location buys
from the real supplier, again when it "sells" the transfer to another location. The
reliable test is a colon in the Contractor field — real suppliers are plain company
names with no colon.

```python
import openpyxl, os, re, glob

def load_all_records(data_folder):
    records = []
    for filepath in sorted(glob.glob(os.path.join(data_folder, "*.xlsx"))):
        fname = os.path.basename(filepath)
        m = re.match(r"(\d{4})\.(\d{2})\.xlsx", fname)
        if not m:
            continue  # skip anything that doesn't match the YYYY.MM.xlsx pattern
        month_key = f"{m.group(1)}.{m.group(2)}"
        wb = openpyxl.load_workbook(filepath, data_only=True)
        ws = wb[wb.sheetnames[0]]
        for row in ws.iter_rows(min_row=4, values_only=True):
            if row[0] is None and row[1] is None:
                continue
            if row[3] != "Purchase invoice":
                continue
            doc_num = str(row[1] or "")
            loc_m = re.match(r"(LU3|LU5|LU7)", doc_num)  # LU4 deliberately excluded
            if not loc_m:
                continue
            contractor = str(row[17] or "")
            if ":" in contractor:
                continue  # internal transfer, not an external purchase
            records.append({
                "month": month_key, "loc": loc_m.group(1),
                "sku": row[4], "product": row[5],
                "qty": row[6] or 0, "price": row[7] or 0,
                "category": row[12] or "Uncategorized",
                "amount": row[27] or 0, "contractor": contractor,
            })
    return records

records = load_all_records(DATA_FOLDER)
MONTHS = sorted(set(r["month"] for r in records))
def month_label(m):  # "2026.08" -> "Aug 2026"
    import datetime
    return datetime.datetime(int(m[:4]), int(m[5:7]), 1).strftime("%b %Y")
MONTH_LABELS = {m: month_label(m) for m in MONTHS}
LOCS = ["LU3", "LU5", "LU7"]
```

Sanity check after loading: print `len(records)` and spot-check that `qty * price`
equals `amount` for a sample of rows (it always has in this data — if it stops
matching, something upstream changed and needs investigating before trusting the
rest of the pipeline).

## Step 2 — Aggregate: monthly spend per location and category

```python
from collections import defaultdict

loc_month_total = defaultdict(lambda: defaultdict(float))
loc_month_cat = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
cat_total = defaultdict(float)
cat_month_spend = defaultdict(lambda: defaultdict(float))

for r in records:
    loc, m, cat, amt = r["loc"], r["month"], r["category"], r["amount"]
    loc_month_total[loc][m] += amt
    loc_month_cat[loc][m][cat] += amt
    cat_total[cat] += amt
    cat_month_spend[cat][m] += amt

top_categories = [c for c, _ in sorted(cat_total.items(), key=lambda x: -x[1])[:8]]

loc_data = {}
for loc in LOCS:
    monthly = [round(loc_month_total[loc].get(m, 0)) for m in MONTHS]
    cat_breakdown = {cat: [round(loc_month_cat[loc][m].get(cat, 0)) for m in MONTHS] for cat in top_categories}
    other_series = []
    for m in MONTHS:
        tot = loc_month_total[loc].get(m, 0)
        top_sum = sum(loc_month_cat[loc][m].get(c, 0) for c in top_categories)
        other_series.append(round(tot - top_sum))
    cat_breakdown["Other"] = other_series
    loc_data[loc] = {"monthly": monthly, "categories": cat_breakdown}

network_monthly = [sum(loc_data[loc]["monthly"][i] for loc in LOCS) for i in range(len(MONTHS))]
cat_month_spend_out = {cat: [round(cat_month_spend[cat].get(m, 0)) for m in MONTHS] for cat in top_categories}
```

## Step 3 — Price-change analyses

Several different angles, each answering a different question. Don't collapse them
into one number — a purchasing manager needs to distinguish "what's hurting the bill
right now" from "which category is driving that" from "which supplier is creeping up
on us" from "is this a slow structural trend" from "how much of each item did we
actually buy".

First build a per-product monthly weighted-average price series (weighted by quantity,
i.e. `total cost / total qty` for that product-month — this matters when the same
product is bought at slightly different unit prices within a month):

```python
prod_month = defaultdict(lambda: defaultdict(lambda: {"qty": 0.0, "amount": 0.0}))
prod_name, prod_cat, prod_total_spend = {}, {}, defaultdict(float)

for r in records:
    key = (r["sku"], r["product"])
    prod_month[key][r["month"]]["qty"] += r["qty"]
    prod_month[key][r["month"]]["amount"] += r["amount"]
    prod_name[key] = r["product"]
    prod_cat[key] = r["category"]
    prod_total_spend[key] += r["amount"]

prod_price_series = {}
for key, months in prod_month.items():
    series = {m: months[m]["amount"] / months[m]["qty"] for m in MONTHS if m in months and months[m]["qty"] > 0}
    prod_price_series[key] = series
```

### 3a. This-month dollar-impact movers (item-level + category rollup)

**What changed, and why:** the first version of this chart summed price-driven cost
impact across the *entire* period (every month-to-month transition, cumulatively).
That produced a confusing bar: an item could rank as a top "cost increase" even though
its price hadn't moved in months — the whole cumulative total came from a single price
jump back in February, invisible in the tooltip. The user caught this immediately
("latest price − last month = 0, so why is this a cost increase?"). The fix: rank
items by **this month's** price effect only —
`(price latest month − price last month purchased) × qty latest month` — computed for
the *most recent* month in the dataset. One number per item, always explains itself.
If you're ever tempted to go back to a cumulative/period metric, don't — show the
current month's effect, and if historical context is wanted, that's what the Item
Price Detail table (3e) is for.

Once the item-level bars existed, the natural next question was "which *category* is
actually driving this?" — 51 small vegetable items moving a little is a different
story from one seafood item moving a lot, but both can produce a similar-looking item
list. The fix is not a new metric — it's the exact same per-item impact number, just
summed into its category instead of ranked individually. Compute both in a single
pass over the data so the two views can never drift apart or double-count:

```python
LATEST = MONTHS[-1]
latest_idx = MONTHS.index(LATEST)
this_month_impact = []
category_impact = defaultdict(float)
category_impact_items = defaultdict(int)
for key, months in prod_month.items():
    if LATEST not in months or months[LATEST]["qty"] <= 0:
        continue
    price_latest = months[LATEST]["amount"] / months[LATEST]["qty"]
    qty_latest = months[LATEST]["qty"]
    prev_month = next((MONTHS[j] for j in range(latest_idx - 1, -1, -1)
                        if MONTHS[j] in months and months[MONTHS[j]]["qty"] > 0), None)
    if prev_month is None:
        continue  # first-ever purchase this month, no baseline to compare
    price_prev = months[prev_month]["amount"] / months[prev_month]["qty"]
    impact = (price_latest - price_prev) * qty_latest
    delta = price_latest - price_prev
    delta_pct = round(delta / price_prev * 100, 1) if price_prev else None
    this_month_impact.append({
        "product": prod_name[key], "impact": round(impact), "total_spend": round(prod_total_spend[key]),
        "m_prev": MONTH_LABELS[prev_month], "m_cur": MONTH_LABELS[LATEST],
        "p_prev": round(price_prev), "p_cur": round(price_latest), "qty_cur": round(qty_latest, 1),
        "delta": round(delta), "delta_pct": delta_pct,
    })
    # Category rollup: same per-item impact, summed into its category. Only items with a
    # nonzero delta count toward n_items — a flat-priced item contributes $0 and shouldn't
    # inflate the "items changed" count shown in the tooltip.
    cat = prod_cat[key] or "Uncategorized"
    category_impact[cat] += impact
    if delta != 0:
        category_impact_items[cat] += 1

dollar_increase = sorted(this_month_impact, key=lambda x: -x["impact"])[:15]
dollar_decrease = sorted(this_month_impact, key=lambda x: x["impact"])[:15]

cat_impact = sorted(
    [{"category": c, "impact": round(v), "n_items": category_impact_items[c]} for c, v in category_impact.items()],
    key=lambda x: -abs(x["impact"])
)
```

`cat_impact` covers every category present in the data (not just `top_categories`) —
this is a rollup over many items so a small category isn't noisy the way a single thin
item would be, and excluding it would hide a real driver. As a sanity check, the sum
of `cat_impact` impacts should equal the sum of `this_month_impact` impacts (small
rounding differences of a few VND are fine — each was rounded independently).

### 3b. Category price index (Laspeyres, base = first month)

**Why not just average price per category?** A raw average blends *price* changes
with *mix* changes — if the kitchen switches from cheap morning glory to pricier
imported greens, "average vegetable price" jumps even though no single item's price
moved. A Laspeyres index holds the **first month's purchased quantities fixed** and
re-prices that same fixed basket in every later month, isolating pure price movement.
This is a different question from 3a's category rollup: 3a tells you which category
moved this month's *bill*, this index tells you which category has a *sustained
directional price trend* independent of volume.

```python
BASE_MONTH = MONTHS[0]
cat_prod_month = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: {"qty": 0.0, "amount": 0.0})))
for r in records:
    key = (r["sku"], r["product"])
    cat_prod_month[r["category"]][key][r["month"]]["qty"] += r["qty"]
    cat_prod_month[r["category"]][key][r["month"]]["amount"] += r["amount"]

cat_index = {}
for cat in top_categories:
    prods = cat_prod_month[cat]
    base_qty, base_price = {}, {}
    for key, months in prods.items():
        if BASE_MONTH in months and months[BASE_MONTH]["qty"] > 0:
            base_qty[key] = months[BASE_MONTH]["qty"]
            base_price[key] = months[BASE_MONTH]["amount"] / months[BASE_MONTH]["qty"]
    series = []
    for m in MONTHS:
        num = den = 0.0
        for key in base_qty:
            months = prods[key]
            if m in months and months[m]["qty"] > 0:
                price_m = months[m]["amount"] / months[m]["qty"]
                num += base_qty[key] * price_m
                den += base_qty[key] * base_price[key]
        series.append(round(num / den * 100, 1) if den > 0 else None)
    cat_index[cat] = {"index": series, "n_skus": len(base_qty),
                       "base_spend": round(sum(base_qty[k] * base_price[k] for k in base_qty))}
```

**Confidence flag:** if a category's base basket (`n_skus`) is small — under ~6 SKUs —
the index is riding on very few products and can look artificially flat or volatile.
The dashboard renders these as dashed lines and calls it out; don't remove that
caveat, and don't feed a thin-basket category into the "biggest sustained price move"
insight without it (the JS already guards this with `n_skus < 6`).

### 3c. Supplier price creep

Spend-weighted average % price change (first vs. last month purchased) across each
supplier's basket — one number per supplier, weighted by how much money actually rides
on each product so a big move on a tiny SKU doesn't dominate.

```python
supplier_prod_month = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: {"qty": 0.0, "amount": 0.0})))
supplier_total = defaultdict(float)
for r in records:
    key = (r["sku"], r["product"])
    supplier_prod_month[r["contractor"]][key][r["month"]]["qty"] += r["qty"]
    supplier_prod_month[r["contractor"]][key][r["month"]]["amount"] += r["amount"]
    supplier_total[r["contractor"]] += r["amount"]

supplier_creep = []
for s, prods in supplier_prod_month.items():
    if supplier_total[s] < 5_000_000:  # materiality floor — avoid noise from one-off small suppliers
        continue
    weighted_sum = weight_sum = 0.0
    n_products = 0
    for key, months in prods.items():
        series = {m: months[m]["amount"] / months[m]["qty"] for m in MONTHS if m in months and months[m]["qty"] > 0}
        if len(series) < 2:
            continue
        ordered = sorted(series.keys())
        p0, p1 = series[ordered[0]], series[ordered[-1]]
        if p0 <= 0:
            continue
        pct = (p1 - p0) / p0 * 100
        spend = sum(months[m]["amount"] for m in months)
        weighted_sum += pct * spend
        weight_sum += spend
        n_products += 1
    if weight_sum > 0 and n_products >= 2:  # need repeat products to trust a "creep" number
        supplier_creep.append({"supplier": s, "pct": round(weighted_sum / weight_sum, 1),
                                "total_spend": round(supplier_total[s]), "n_products": n_products})

supplier_creep = sorted(supplier_creep, key=lambda x: -abs(x["pct"]))[:20]
```

### 3d. Top % movers

Simple first-vs-last-month % change, filtered to products with at least ₫1,000,000
total spend over the period — without this floor, a product bought twice for a few
thousand VND can show a 200% swing that means nothing.

```python
pct_movers = []
for key, series in prod_price_series.items():
    if prod_total_spend[key] < 1_000_000 or len(series) < 2:
        continue
    ordered = sorted(series.keys())
    p0, p1 = series[ordered[0]], series[ordered[-1]]
    if p0 <= 0:
        continue
    pct = (p1 - p0) / p0 * 100
    pct_movers.append({"product": prod_name[key], "pct": round(pct, 1), "p0": round(p0, 1), "p1": round(p1, 1),
                        "m0": MONTH_LABELS[ordered[0]], "m1": MONTH_LABELS[ordered[-1]],
                        "total_spend": round(prod_total_spend[key])})
pct_movers = sorted(pct_movers, key=lambda x: -abs(x["pct"]))[:20]
```

### 3e. Item price detail (every item, every month)

The full item × month price matrix backing the filterable/searchable table. Include
**every** product with at least one valid price point — this is the one view where
completeness matters more than materiality filtering, since the user filters and
searches interactively. This table is network-wide (all locations combined) — it
answers "what did we pay for this item". For "how much of this item did each store
buy", see 3f below.

```python
item_matrix = []
for key, series in prod_price_series.items():
    prices = [round(series[m]) if m in series else None for m in MONTHS]
    item_matrix.append({"product": prod_name[key], "category": prod_cat[key] or "Uncategorized",
                         "prices": prices, "total_spend": round(prod_total_spend[key])})
item_matrix.sort(key=lambda x: -x["total_spend"])
item_categories = sorted(set(it["category"] for it in item_matrix))
```

### 3f. Item volume/spend by store

A different question from 3e: instead of weighted-average *price* (network-wide only),
this shows raw *quantity* and *spend*, broken out per store, so a manager can see e.g.
"how much beef did LU5 actually buy each month" — not just "what did beef cost". Build
one row set per location (plus an "all locations" rollup), each containing both a qty
series and an amount series so the dashboard can toggle between the two without
recomputing:

```python
loc_prod_month = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: {"qty": 0.0, "amount": 0.0})))
for r in records:
    key = (r["sku"], r["product"])
    loc_prod_month[r["loc"]][key][r["month"]]["qty"] += r["qty"]
    loc_prod_month[r["loc"]][key][r["month"]]["amount"] += r["amount"]

def build_item_store_rows(loc_filter=None):
    # loc_filter=None aggregates across all locations (the "NETWORK" / All Locations view)
    agg = defaultdict(lambda: defaultdict(lambda: {"qty": 0.0, "amount": 0.0}))
    for loc in (LOCS if loc_filter is None else [loc_filter]):
        for key, months in loc_prod_month[loc].items():
            for m, v in months.items():
                agg[key][m]["qty"] += v["qty"]
                agg[key][m]["amount"] += v["amount"]
    rows = []
    for key, months in agg.items():
        qty_series = [round(months[m]["qty"], 1) if m in months else 0 for m in MONTHS]
        amt_series = [round(months[m]["amount"]) if m in months else 0 for m in MONTHS]
        total_qty, total_amt = round(sum(qty_series), 1), round(sum(amt_series))
        if total_amt <= 0 and total_qty <= 0:
            continue  # this item was never purchased at this location — omit rather than show a blank row
        rows.append({"product": prod_name[key], "category": prod_cat[key] or "Uncategorized",
                     "qty": qty_series, "amount": amt_series,
                     "total_qty": total_qty, "total_amount": total_amt})
    rows.sort(key=lambda x: -x["total_amount"])
    return rows

item_store_matrix = {"NETWORK": build_item_store_rows(None)}
for loc in LOCS:
    item_store_matrix[loc] = build_item_store_rows(loc)
```

Sanity check: `sum(it["total_amount"] for it in item_store_matrix["NETWORK"])` should
equal the sum of the three per-location totals, and should match the network total
spend from Step 2. Also expect the row counts to differ per location — not every store
buys every item (e.g. `LU3=397, LU5=323, LU7=321` rows vs `NETWORK=446` in one run) —
that's correct, not a bug; a location with fewer distinct SKUs just has a smaller menu
or supplier list.

## Step 4 — Assemble the DATA payload and write the HTML

```python
import json

payload = {
    "months": [MONTH_LABELS[m] for m in MONTHS],
    "locations": LOCS,
    "loc_data": loc_data,
    "network_monthly": network_monthly,
    "top_categories": top_categories,
    "cat_index": cat_index,
    "cat_month_spend": cat_month_spend_out,
    "dollar_increase": dollar_increase,
    "dollar_decrease": dollar_decrease,
    "cat_impact": cat_impact,
    "pct_movers": pct_movers,
    "supplier_creep": supplier_creep,
    "item_matrix": item_matrix,
    "item_categories": item_categories,
    "item_store_matrix": item_store_matrix,
}
DATA_JSON = json.dumps(payload, ensure_ascii=False)

html = HTML_TEMPLATE_BEFORE + "const DATA = " + DATA_JSON + ";" + HTML_TEMPLATE_AFTER
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(html)
print(f"Wrote {OUTPUT_FILE} — {len(html):,} chars, {len(MONTHS)} months, {len(item_matrix)} items, "
      f"₫{sum(network_monthly):,} total network spend.")
```

`HTML_TEMPLATE_BEFORE` and `HTML_TEMPLATE_AFTER` are the two halves of the dashboard
below, split at the point where the `DATA` payload gets injected. Everything is
self-contained: Chart.js loads from the jsdelivr CDN (no `integrity=` attribute — that
silently breaks the chart rendering), the dark theme follows the L-Concepts palette
already used in the `pl-dashboard` skill (green `#1D9E75` / grey `#9ca3af` / amber
`#f59e0b` / red `#E24B4A`), and every chart goes through a `makeChart()` wrapper that
destroys stale Chart.js instances before creating new ones — skipping that causes
charts to silently fail to update when the location tab changes.

Note on file size: `item_store_matrix` adds every item × month × store combination to
the payload, which grows the output file noticeably (roughly 110KB → 450KB on a
7-month, ~450-item dataset). That's still a normal size for a local, self-contained
HTML file to open in a browser — don't try to "optimize" it away by dropping data
unless the user asks.

**`HTML_TEMPLATE_BEFORE`** (everything from `<!DOCTYPE html>` through the opening
`<script>` tag, right before `const DATA = `):

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Purchasing Dashboard — LU3 / LU5 / LU7</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.5.1/dist/chart.umd.min.js"></script>
<style>
  :root{
    --green:#1D9E75; --grey:#9ca3af; --amber:#f59e0b; --red:#E24B4A;
    --lu3:#1D9E75; --lu5:#f59e0b; --lu7:#3B82F6;
    --bg:#0f1115; --panel:#171a21; --panel2:#1e222b; --border:#2a2f3a;
    --text:#e8eaed; --sub:#9aa1ac;
  }
  *{box-sizing:border-box;}
  body{margin:0;background:var(--bg);color:var(--text);font-family:'Segoe UI',Helvetica,Arial,sans-serif;}
  header{padding:24px 28px 16px;border-bottom:1px solid var(--border);position:sticky;top:0;background:var(--bg);z-index:20;}
  header h1{margin:0 0 4px;font-size:22px;font-weight:700;}
  header p{margin:0;color:var(--sub);font-size:13px;}
  .wrap{max-width:1280px;margin:0 auto;padding:20px 24px 60px;}
  .tabs{display:flex;gap:6px;margin:16px 0 20px;flex-wrap:wrap;}
  .tab{padding:8px 16px;border-radius:8px;background:var(--panel);border:1px solid var(--border);color:var(--sub);cursor:pointer;font-size:13px;font-weight:600;transition:.15s;}
  .tab:hover{color:var(--text);}
  .tab.active{background:var(--green);color:#06231a;border-color:var(--green);}
  .tab.active.lu5{background:var(--amber);color:#2b1a02;border-color:var(--amber);}
  .tab.active.lu7{background:var(--lu7);color:#04122b;border-color:var(--lu7);}
  .kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:22px;}
  .kpi{background:var(--panel);border:1px solid var(--border);border-radius:12px;padding:16px 18px;}
  .kpi .label{font-size:11px;text-transform:uppercase;letter-spacing:.04em;color:var(--sub);margin-bottom:6px;}
  .kpi .value{font-size:22px;font-weight:700;}
  .kpi .sub{font-size:12px;margin-top:4px;color:var(--sub);}
  .pos{color:var(--red);} .neg{color:var(--green);}
  .card{background:var(--panel);border:1px solid var(--border);border-radius:14px;padding:20px;margin-bottom:20px;}
  .card h2{margin:0 0 4px;font-size:16px;}
  .card .desc{color:var(--sub);font-size:12.5px;margin:0 0 14px;}
  .grid2{display:grid;grid-template-columns:1fr 1fr;gap:20px;}
  canvas{max-width:100%;}
  .callout{background:linear-gradient(135deg,#1c2a24,#171a21);border:1px solid #2b4a3c;border-radius:14px;padding:20px 22px;margin-bottom:22px;}
  .callout h2{margin:0 0 10px;font-size:16px;color:#7fe0bd;}
  .callout ul{margin:0;padding-left:18px;}
  .callout li{margin-bottom:8px;font-size:13.5px;line-height:1.5;color:#dfe3e8;}
  .callout b{color:#fff;}
  table{width:100%;border-collapse:collapse;font-size:12.5px;}
  th{text-align:left;color:var(--sub);font-weight:600;font-size:11px;text-transform:uppercase;letter-spacing:.03em;padding:8px 10px;border-bottom:1px solid var(--border);}
  td{padding:8px 10px;border-bottom:1px solid #23262f;}
  tr:hover td{background:#1c2029;}
  .num{text-align:right;font-variant-numeric:tabular-nums;}
  .badge{display:inline-block;padding:2px 8px;border-radius:20px;font-size:11px;font-weight:700;}
  .badge.up{background:rgba(226,75,74,.15);color:#f28c8b;}
  .badge.down{background:rgba(29,158,117,.15);color:#4fd6ab;}
  .pill{font-size:10px;background:#33261080;color:#f6bf6b;padding:2px 7px;border-radius:20px;margin-left:8px;}
  .subtabs{display:flex;gap:6px;margin-bottom:16px;flex-wrap:wrap;}
  .subtab{padding:6px 14px;border-radius:20px;background:var(--panel2);border:1px solid var(--border);color:var(--sub);cursor:pointer;font-size:12.5px;font-weight:600;}
  .subtab.active{background:#2c3542;color:#fff;border-color:#3d4a5c;}
  .note{font-size:11.5px;color:var(--sub);margin-top:10px;line-height:1.5;}
  .price-up{background:rgba(226,75,74,.20);color:#f6b8b7;font-weight:600;}
  .price-down{background:rgba(29,158,117,.20);color:#8fe9c9;font-weight:600;}
  .legend-inline{display:flex;gap:16px;align-items:center;font-size:11.5px;color:var(--sub);}
  .legend-swatch{display:inline-block;width:10px;height:10px;border-radius:3px;margin-right:5px;vertical-align:-1px;}
  .flex-between{display:flex;justify-content:space-between;align-items:baseline;flex-wrap:wrap;gap:8px;}
</style>
</head>
<body>
<header>
  <h1>Purchasing Dashboard — LU3 / LU5 / LU7</h1>
  <p id="headerSub">External-supplier purchase invoices only (internal LU4 transfers excluded)</p>
</header>
<div class="wrap">

  <div class="callout">
    <h2 id="calloutTitle">What actually happened</h2>
    <ul id="insights"></ul>
  </div>

  <div class="tabs" id="locTabs"></div>
  <div class="kpis" id="kpiRow"></div>

  <div class="card">
    <div class="flex-between">
      <div><h2 id="trendTitle">Monthly Purchasing</h2><p class="desc">External supplier spend, VND</p></div>
    </div>
    <canvas id="trendChart" height="90"></canvas>
  </div>

  <div class="card">
    <h2 id="catTitle">Spend by Category</h2>
    <p class="desc">Top 8 categories by spend, remainder grouped as "Other"</p>
    <canvas id="catChart" height="100"></canvas>
  </div>

  <div class="card">
    <div class="flex-between">
      <div><h2 id="itemStoreTitle">Item Detail by Month — Volume & Spend</h2><p class="desc">Every item purchased at the location selected above, month by month. Toggle between $ spend and quantity purchased.</p></div>
      <div class="subtabs" id="itemStoreMetricTabs" style="margin:0;">
        <div class="subtab active" data-m="amount">Amount (₫)</div>
        <div class="subtab" data-m="qty">Quantity</div>
      </div>
    </div>
    <div class="flex-between" style="margin:14px 0;gap:12px;">
      <div style="display:flex;gap:8px;flex-wrap:wrap;align-items:center;">
        <select id="itemStoreCatFilter" style="background:var(--panel2);color:var(--text);border:1px solid var(--border);border-radius:8px;padding:6px 10px;font-size:12.5px;"></select>
        <input id="itemStoreSearch" type="text" placeholder="Search item..." style="background:var(--panel2);color:var(--text);border:1px solid var(--border);border-radius:8px;padding:6px 10px;font-size:12.5px;min-width:200px;">
      </div>
      <div class="note" id="itemStoreCount" style="margin:0;"></div>
    </div>
    <div style="max-height:600px;overflow:auto;">
      <table>
        <thead><tr id="itemStoreHeadRow"><th>Product</th><th>Category</th></tr></thead>
        <tbody id="itemStoreTable"></tbody>
      </table>
    </div>
  </div>

  <h1 style="font-size:18px;margin:36px 0 4px;">Price Change Analysis</h1>
  <p style="color:var(--sub);font-size:13px;margin:0 0 16px;">Network-wide (LU3+LU5+LU7 combined) — separating true price movement from volume/mix shifts</p>

  <div class="subtabs" id="priceTabs">
    <div class="subtab active" data-p="impact">Dollar-Impact Movers</div>
    <div class="subtab" data-p="category">Category Price Index</div>
    <div class="subtab" data-p="supplier">Supplier Price Creep</div>
    <div class="subtab" data-p="pct">Top % Movers</div>
    <div class="subtab" data-p="detail">Item Price Detail</div>
  </div>

  <div id="panel-impact" class="pricePanel">
    <div class="card">
      <h2 id="catImpactTitle">Price impact by category</h2>
      <p class="desc">Same formula, rolled up by category: (price this month − price last month purchased) × qty this month, summed across every item in the category that had a price change. Shows which categories are driving this month's cost swing before drilling into individual items below.</p>
      <canvas id="catImpactChart" height="90"></canvas>
    </div>
    <div class="card">
      <h2 id="impactTitle">How much price changes moved this month's bill</h2>
      <p class="desc" id="impactDesc">(price this month − price last month purchased) × qty this month. One number per item, tied to the latest month only — no historical carry-over, so the bar always explains what's driving that item's cost right now.</p>
      <div class="grid2">
        <div>
          <h3 style="font-size:13px;color:#f28c8b;">Cost increases (top 15)</h3>
          <canvas id="impactUpChart" height="220"></canvas>
        </div>
        <div>
          <h3 style="font-size:13px;color:#4fd6ab;">Cost decreases / savings (top 15)</h3>
          <canvas id="impactDownChart" height="220"></canvas>
        </div>
      </div>
    </div>
  </div>

  <div id="panel-category" class="pricePanel" style="display:none;">
    <div class="card">
      <h2 id="catIndexTitle">Category price index</h2>
      <p class="desc">Laspeyres-style index: holds the first month's purchase quantities fixed and re-prices them each month, so the line shows pure price movement — not the effect of buying more or less.</p>
      <canvas id="catIndexChart" height="110"></canvas>
      <div class="note" id="catIndexNote"></div>
    </div>
    <div class="card">
      <h2>Category spend, for context</h2>
      <p class="desc">Actual monthly spend by category — compare against the index above. A category can show flat prices and exploding spend (that's a volume story, not a price story).</p>
      <canvas id="catSpendChart" height="110"></canvas>
    </div>
  </div>

  <div id="panel-supplier" class="pricePanel" style="display:none;">
    <div class="card">
      <h2>Supplier price creep</h2>
      <p class="desc">Spend-weighted average price change (first vs. last month purchased) across each supplier's basket. Suppliers with <₫5M total spend or fewer than 2 repeat products are excluded to avoid noise.</p>
      <table>
        <thead><tr><th>Supplier</th><th class="num">Price change</th><th class="num">Total spend</th><th class="num"># Products</th></tr></thead>
        <tbody id="supplierTable"></tbody>
      </table>
    </div>
  </div>

  <div id="panel-pct" class="pricePanel" style="display:none;">
    <div class="card">
      <h2>Biggest % price movers</h2>
      <p class="desc">First vs. last month purchased, weighted-average price. Filtered to products with ≥₫1M total spend over the period.</p>
      <table>
        <thead><tr><th>Product</th><th class="num">Change</th><th class="num">Price (start → end)</th><th class="num">Total spend</th></tr></thead>
        <tbody id="pctTable"></tbody>
      </table>
    </div>
  </div>

  <div id="panel-detail" class="pricePanel" style="display:none;">
    <div class="card">
      <h2>Item price detail, by month</h2>
      <p class="desc">Weighted-average price (VND) per month for every item. Sorted by total spend by default — click "Total Spend" to flip direction. Each cell is colored against the item's previous purchased month, so you can see exactly which month a price move happened in — not just where it landed.</p>
      <div class="flex-between" style="margin-bottom:14px;gap:12px;">
        <div style="display:flex;gap:8px;flex-wrap:wrap;align-items:center;">
          <select id="detailCatFilter" style="background:var(--panel2);color:var(--text);border:1px solid var(--border);border-radius:8px;padding:6px 10px;font-size:12.5px;"></select>
          <input id="detailSearch" type="text" placeholder="Search item..." style="background:var(--panel2);color:var(--text);border:1px solid var(--border);border-radius:8px;padding:6px 10px;font-size:12.5px;min-width:200px;">
          <span class="legend-inline"><span><span class="legend-swatch" style="background:#E24B4A;"></span>price up vs prior purchase</span><span><span class="legend-swatch" style="background:#1D9E75;"></span>price down</span></span>
        </div>
        <div class="note" id="detailCount" style="margin:0;"></div>
      </div>
      <div style="max-height:600px;overflow:auto;">
        <table>
          <thead><tr id="detailHeadRow"><th>Product</th><th>Category</th></tr></thead>
          <tbody id="detailTable"></tbody>
        </table>
      </div>
    </div>
  </div>

</div>

<script>
```

**`HTML_TEMPLATE_AFTER`** (everything from right after the `DATA` payload's closing
`;` through `</html>`):

```html


const fmt = v => new Intl.NumberFormat('en-US',{maximumFractionDigits:0}).format(v);
const fmtM = v => (v/1e6).toFixed(0)+'M';
const fmtVND = v => fmt(v) + ' ₫';

const chartReg = {};
function makeChart(id, cfg){
  const el = document.getElementById(id);
  if(!el) return null;
  const existing = Chart.getChart(el);
  if(existing) existing.destroy();
  if(chartReg[id]){ try{chartReg[id].destroy();}catch(e){} }
  const c = new Chart(el, cfg);
  chartReg[id] = c;
  return c;
}

const LOC_COLORS = {LU3:'#1D9E75', LU5:'#f59e0b', LU7:'#3B82F6', NETWORK:'#8b5cf6'};
const CAT_COLORS = ['#1D9E75','#f59e0b','#3B82F6','#E24B4A','#a78bfa','#f472b6','#38bdf8','#facc15','#6b7280'];

let currentView = 'NETWORK';

function buildTabs(){
  const el = document.getElementById('locTabs');
  const views = ['NETWORK', ...DATA.locations];
  el.innerHTML = views.map(v => `<div class="tab ${v===currentView?'active':''} ${v.toLowerCase()}" data-v="${v}">${v==='NETWORK'?'All Locations':v}</div>`).join('');
  el.querySelectorAll('.tab').forEach(t => t.addEventListener('click', () => { currentView = t.dataset.v; render(); }));
}

function getMonthly(view){
  return view==='NETWORK' ? DATA.network_monthly : DATA.loc_data[view].monthly;
}

function buildKpis(){
  const monthly = getMonthly(currentView);
  const total = monthly.reduce((a,b)=>a+b,0);
  const avg = total/monthly.length;
  const latest = monthly[monthly.length-1];
  const prev = monthly[monthly.length-2];
  const mom = ((latest-prev)/prev*100);
  const peakIdx = monthly.indexOf(Math.max(...monthly));
  const el = document.getElementById('kpiRow');
  el.innerHTML = `
    <div class="kpi"><div class="label">Total Spend (${monthly.length} mo)</div><div class="value">${fmtVND(total)}</div><div class="sub">${currentView==='NETWORK'?'LU3+LU5+LU7':currentView}</div></div>
    <div class="kpi"><div class="label">Avg / Month</div><div class="value">${fmtVND(Math.round(avg))}</div><div class="sub">across ${monthly.length} months</div></div>
    <div class="kpi"><div class="label">Latest Month (${DATA.months[DATA.months.length-1]})</div><div class="value">${fmtVND(latest)}</div><div class="sub ${mom>=0?'pos':'neg'}">${mom>=0?'▲':'▼'} ${Math.abs(mom).toFixed(1)}% vs prior month</div></div>
    <div class="kpi"><div class="label">Peak Month</div><div class="value">${DATA.months[peakIdx]}</div><div class="sub">${fmtVND(monthly[peakIdx])}</div></div>
  `;
}

function buildTrendChart(){
  document.getElementById('trendTitle').innerText = 'Monthly Purchasing — ' + (currentView==='NETWORK'?'All Locations':currentView);
  let datasets;
  if(currentView==='NETWORK'){
    datasets = DATA.locations.map(loc => ({
      label: loc, data: DATA.loc_data[loc].monthly,
      backgroundColor: LOC_COLORS[loc], stack:'s'
    }));
  } else {
    datasets = [{label: currentView, data: DATA.loc_data[currentView].monthly, backgroundColor: LOC_COLORS[currentView]}];
  }
  makeChart('trendChart', {
    type:'bar',
    data:{labels: DATA.months, datasets},
    options:{
      responsive:true,
      plugins:{legend:{display: currentView==='NETWORK', labels:{color:'#e8eaed'}}, tooltip:{callbacks:{label: ctx => ctx.dataset.label+': '+fmtVND(ctx.raw)}}},
      scales:{
        x:{stacked:true, ticks:{color:'#9aa1ac'}, grid:{color:'#2a2f3a'}},
        y:{stacked:true, ticks:{color:'#9aa1ac', callback:v=>fmtM(v)}, grid:{color:'#2a2f3a'}}
      }
    }
  });
}

function buildCatChart(){
  document.getElementById('catTitle').innerText = 'Spend by Category — ' + (currentView==='NETWORK'?'All Locations':currentView);
  const cats = [...DATA.top_categories, 'Other'];
  let series;
  if(currentView==='NETWORK'){
    series = cats.map(cat => DATA.months.map((_,i) => DATA.locations.reduce((sum,loc)=> sum + (DATA.loc_data[loc].categories[cat] ? DATA.loc_data[loc].categories[cat][i] : 0), 0)));
  } else {
    series = cats.map(cat => DATA.loc_data[currentView].categories[cat] || DATA.months.map(()=>0));
  }
  const datasets = cats.map((cat,i) => ({label:cat, data:series[i], backgroundColor: CAT_COLORS[i], stack:'s'}));
  makeChart('catChart', {
    type:'bar',
    data:{labels:DATA.months, datasets},
    options:{
      responsive:true,
      plugins:{legend:{labels:{color:'#e8eaed', boxWidth:12, font:{size:11}}}, tooltip:{callbacks:{label: ctx => ctx.dataset.label+': '+fmtVND(ctx.raw)}}},
      scales:{
        x:{stacked:true, ticks:{color:'#9aa1ac'}, grid:{display:false}},
        y:{stacked:true, ticks:{color:'#9aa1ac', callback:v=>fmtM(v)}, grid:{color:'#2a2f3a'}}
      }
    }
  });
}

function buildInsights(){
  const net = DATA.network_monthly;
  const months = DATA.months;
  const firstLabel = months[0], lastLabel = months[months.length-1];
  const total = net.reduce((a,b)=>a+b,0);

  document.getElementById('headerSub').innerText =
    `External-supplier purchase invoices only (internal LU4 transfers excluded) · ${firstLabel}–${lastLabel}`;
  document.getElementById('calloutTitle').innerText = `What actually happened, ${firstLabel}–${lastLabel}`;

  const lines = ['<li><b>LU4 (central kitchen) closed permanently in March 2026</b> and is excluded from this dashboard — all figures below are LU3/LU5/LU7 only.</li>'];

  // Biggest month-over-month spend jump (skip first month, no prior to compare) — only call it
  // out if it clears a noise threshold, so a normal month doesn't get a manufactured "insight".
  if(net.length >= 2){
    let peakIdx = -1, peakPct = -Infinity;
    for(let i=1;i<net.length;i++){
      const pct = (net[i]-net[i-1])/net[i-1]*100;
      if(pct > peakPct){ peakPct = pct; peakIdx = i; }
    }
    if(peakPct > 15){
      // Which top category drove the most of that month's $ increase? Check spend AND price index
      // so we don't conflate "bought more" with "paid more" — that's the whole point of this dashboard.
      let driverCat=null, driverDelta=-Infinity;
      DATA.top_categories.forEach(cat=>{
        const s = DATA.cat_month_spend[cat];
        const delta = s[peakIdx]-s[peakIdx-1];
        if(delta > driverDelta){ driverDelta = delta; driverCat = cat; }
      });
      const driverIdx = driverCat ? DATA.cat_index[driverCat] : null;
      const priceMoved = driverIdx && Math.abs(driverIdx.index[peakIdx] - driverIdx.index[peakIdx-1]) > 3;
      lines.push(`<li><b>${months[peakIdx]} spend jumped ${peakPct.toFixed(0)}%</b> vs ${months[peakIdx-1]} (₫${fmt(net[peakIdx-1])} → ₫${fmt(net[peakIdx])}). Biggest single driver: <b>${driverCat}</b> (+₫${fmt(driverDelta)} that month) — ${priceMoved ? 'and its price index moved too, so at least part of this is a price story.' : 'but its price index barely moved, so this looks like a volume/mix story, not a price story. Check the Category Price Index tab before assuming a supplier raised prices.'}</li>`);
    }
  }

  // Category with the largest sustained price move (Laspeyres index vs first month), among
  // categories with a large enough base basket to trust (see cat_index n_skus).
  let bigMoveCat=null, bigMoveVal=0;
  DATA.top_categories.forEach(cat=>{
    const idx = DATA.cat_index[cat];
    if(idx.n_skus < 6) return;
    const change = idx.index[idx.index.length-1]-100;
    if(Math.abs(change) > Math.abs(bigMoveVal)){ bigMoveVal = change; bigMoveCat = cat; }
  });
  if(bigMoveCat){
    lines.push(`<li><b>${bigMoveCat}</b> shows the largest sustained price move of any well-sampled category: ${bigMoveVal>=0?'+':''}${bigMoveVal.toFixed(1)}% since ${firstLabel} (Laspeyres index, ${DATA.cat_index[bigMoveCat].n_skus} SKUs in the base basket).</li>`);
  }

  lines.push(`<li>Total external-supplier purchasing across LU3+LU5+LU7, ${firstLabel}–${lastLabel}: <b>₫${fmt(total)}</b> (avg ₫${fmt(Math.round(total/net.length))}/month).</li>`);

  document.getElementById('insights').innerHTML = lines.join('\n');
}

function buildCatIndexChart(){
  document.getElementById('catIndexTitle').innerText = `Category price index (${DATA.months[0]} = 100)`;
  const datasets = DATA.top_categories.map((cat,i) => ({
    label: cat + ' (' + DATA.cat_index[cat].n_skus + ' SKUs)',
    data: DATA.cat_index[cat].index,
    borderColor: CAT_COLORS[i], backgroundColor:'transparent', tension:.3,
    borderDash: DATA.cat_index[cat].n_skus < 6 ? [5,4] : [],
  }));
  makeChart('catIndexChart', {
    type:'line',
    data:{labels:DATA.months, datasets},
    options:{
      responsive:true,
      plugins:{legend:{labels:{color:'#e8eaed', boxWidth:12, font:{size:11}}}},
      scales:{
        x:{ticks:{color:'#9aa1ac'}, grid:{color:'#2a2f3a'}},
        y:{ticks:{color:'#9aa1ac'}, grid:{color:'#2a2f3a'}, suggestedMin:80, suggestedMax:110}
      }
    }
  });
  const thinCats = DATA.top_categories.filter(cat => DATA.cat_index[cat].n_skus < 6);
  document.getElementById('catIndexNote').innerHTML = thinCats.length
    ? `Dashed lines (${thinCats.map(c => c + ' — ' + DATA.cat_index[c].n_skus + ' SKUs').join(', ')}) are based on a thin ${DATA.months[0]} basket — treat as low-confidence. Their real story may be volume growth, shown in the spend chart below, not price.`
    : '';
}

function buildCatSpendChart(){
  const datasets = DATA.top_categories.map((cat,i) => ({
    label: cat, data: DATA.cat_month_spend[cat], borderColor: CAT_COLORS[i], backgroundColor:'transparent', tension:.3
  }));
  makeChart('catSpendChart', {
    type:'line',
    data:{labels:DATA.months, datasets},
    options:{
      responsive:true,
      plugins:{legend:{labels:{color:'#e8eaed', boxWidth:12, font:{size:11}}}, tooltip:{callbacks:{label: ctx => ctx.dataset.label+': '+fmtVND(ctx.raw)}}},
      scales:{
        x:{ticks:{color:'#9aa1ac'}, grid:{color:'#2a2f3a'}},
        y:{ticks:{color:'#9aa1ac', callback:v=>fmtM(v)}, grid:{color:'#2a2f3a'}}
      }
    }
  });
}

function impactTooltip(d){
  const arrow = d.delta > 0 ? '▲' : d.delta < 0 ? '▼' : '→';
  const pctStr = (d.delta_pct===null) ? '' : ` (${d.delta_pct>=0?'+':''}${d.delta_pct}%)`;
  return [
    'This month\'s $ impact: ' + (d.impact>=0?'+':'') + fmtVND(d.impact),
    `Price: ${fmt(d.p_prev)} ₫ (${d.m_prev}) ${arrow} ${fmt(d.p_cur)} ₫ (${d.m_cur})`,
    `Change: ${d.delta>=0?'+':''}${fmt(d.delta)} ₫${pctStr}  ×  qty ${fmt(d.qty_cur)}`,
    'Total spend (period): ' + fmtVND(d.total_spend)
  ];
}

function buildImpactCharts(){
  const latestLabel = DATA.months[DATA.months.length-1];
  document.getElementById('impactTitle').innerText = `How much price changes moved ${latestLabel}'s bill`;
  makeChart('impactUpChart', {
    type:'bar',
    data:{labels: DATA.dollar_increase.map(d=>d.product.split('/')[0].trim()), datasets:[{data: DATA.dollar_increase.map(d=>d.impact), backgroundColor:'#E24B4A'}]},
    options:{indexAxis:'y', plugins:{legend:{display:false}, tooltip:{callbacks:{label: ctx => impactTooltip(DATA.dollar_increase[ctx.dataIndex])}}},
      scales:{x:{ticks:{color:'#9aa1ac', callback:v=>fmtM(v)}, grid:{color:'#2a2f3a'}}, y:{ticks:{color:'#e8eaed', font:{size:10.5}}, grid:{display:false}}}}
  });
  makeChart('impactDownChart', {
    type:'bar',
    data:{labels: DATA.dollar_decrease.map(d=>d.product.split('/')[0].trim()), datasets:[{data: DATA.dollar_decrease.map(d=>d.impact), backgroundColor:'#1D9E75'}]},
    options:{indexAxis:'y', plugins:{legend:{display:false}, tooltip:{callbacks:{label: ctx => impactTooltip(DATA.dollar_decrease[ctx.dataIndex])}}},
      scales:{x:{ticks:{color:'#9aa1ac', callback:v=>fmtM(v)}, grid:{color:'#2a2f3a'}}, y:{ticks:{color:'#e8eaed', font:{size:10.5}}, grid:{display:false}}}}
  });
}

function buildCatImpactChart(){
  const latestLabel = DATA.months[DATA.months.length-1];
  document.getElementById('catImpactTitle').innerText = `Price impact by category — ${latestLabel}`;
  const sorted = DATA.cat_impact.slice().sort((a,b) => b.impact - a.impact);
  makeChart('catImpactChart', {
    type:'bar',
    data:{
      labels: sorted.map(d=>d.category),
      datasets:[{
        data: sorted.map(d=>d.impact),
        backgroundColor: sorted.map(d=> d.impact>=0 ? '#E24B4A' : '#1D9E75')
      }]
    },
    options:{
      indexAxis:'y',
      plugins:{
        legend:{display:false},
        tooltip:{callbacks:{label: ctx => {
          const d = sorted[ctx.dataIndex];
          return [
            (d.impact>=0?'+':'') + fmtVND(d.impact),
            `${d.n_items} item${d.n_items===1?'':'s'} with a price change vs their last purchased month`
          ];
        }}}
      },
      scales:{
        x:{ticks:{color:'#9aa1ac', callback:v=>fmtM(v)}, grid:{color:'#2a2f3a'}},
        y:{ticks:{color:'#e8eaed'}, grid:{display:false}}
      }
    }
  });
}

function buildSupplierTable(){
  const rows = DATA.supplier_creep.map(s => `
    <tr>
      <td>${s.supplier}</td>
      <td class="num"><span class="badge ${s.pct>=0?'up':'down'}">${s.pct>=0?'▲':'▼'} ${Math.abs(s.pct).toFixed(1)}%</span></td>
      <td class="num">${fmtVND(s.total_spend)}</td>
      <td class="num">${s.n_products}</td>
    </tr>`).join('');
  document.getElementById('supplierTable').innerHTML = rows;
}

function buildPctTable(){
  const rows = DATA.pct_movers.map(p => `
    <tr>
      <td>${p.product}</td>
      <td class="num"><span class="badge ${p.pct>=0?'up':'down'}">${p.pct>=0?'▲':'▼'} ${Math.abs(p.pct).toFixed(1)}%</span></td>
      <td class="num">${fmt(p.p0)} (${p.m0}) → ${fmt(p.p1)} (${p.m1})</td>
      <td class="num">${fmtVND(p.total_spend)}</td>
    </tr>`).join('');
  document.getElementById('pctTable').innerHTML = rows;
}

// --- Item Price Detail table ---
let detailSort = {key:'total_spend', dir:-1};

function buildDetailFilterOptions(){
  const sel = document.getElementById('detailCatFilter');
  const cats = ['All Categories', ...DATA.item_categories];
  sel.innerHTML = cats.map(c => `<option value="${c}">${c}</option>`).join('');
  sel.value = 'All Categories';
}

function buildDetailHead(){
  const row = document.getElementById('detailHeadRow');
  const cells = ['<th data-k="product">Product</th>', '<th data-k="category">Category</th>']
    .concat(DATA.months.map((m,i) => `<th class="num" data-k="m${i}">${m.split(' ')[0]}</th>`))
    .concat(['<th class="num" data-k="total_spend" style="cursor:pointer;">Total Spend ' + (detailSort.key==='total_spend' ? (detailSort.dir<0?'▼':'▲') : '') + '</th>']);
  row.innerHTML = cells.join('');
  row.querySelectorAll('th[data-k]').forEach(th => th.addEventListener('click', () => {
    const k = th.dataset.k;
    if(detailSort.key===k) detailSort.dir *= -1; else detailSort = {key:k, dir: k==='product'||k==='category' ? 1 : -1};
    buildDetailHead();
    renderDetailRows();
  }));
}

function renderDetailRows(){
  const catFilter = document.getElementById('detailCatFilter').value;
  const q = document.getElementById('detailSearch').value.trim().toLowerCase();
  let rows = DATA.item_matrix.filter(it =>
    (catFilter==='All Categories' || it.category===catFilter) &&
    (q==='' || it.product.toLowerCase().includes(q))
  );
  const k = detailSort.key, dir = detailSort.dir;
  rows = rows.slice().sort((a,b) => {
    let av, bv;
    if(k==='product' || k==='category'){ av=a[k]; bv=b[k]; return dir*av.localeCompare(bv); }
    else if(k==='total_spend'){ av=a.total_spend; bv=b.total_spend; }
    else { const idx = parseInt(k.slice(1)); av = a.prices[idx]===null?-Infinity:a.prices[idx]; bv = b.prices[idx]===null?-Infinity:b.prices[idx]; }
    return dir*(av-bv);
  });
  document.getElementById('detailCount').innerText = rows.length + ' of ' + DATA.item_matrix.length + ' items';
  document.getElementById('detailTable').innerHTML = rows.map(it => {
    let lastValid = null;
    const priceCells = it.prices.map(p => {
      if(p===null) return `<td class="num" style="color:#565d6b">—</td>`;
      let cls = '';
      if(lastValid !== null){
        if(p > lastValid) cls = 'price-up';
        else if(p < lastValid) cls = 'price-down';
      }
      lastValid = p;
      return `<td class="num ${cls}">${fmt(p)}</td>`;
    }).join('');
    return `<tr><td>${it.product}</td><td>${it.category}</td>${priceCells}<td class="num">${fmtVND(it.total_spend)}</td></tr>`;
  }).join('');
}

function buildItemDetailTable(){
  buildDetailFilterOptions();
  buildDetailHead();
  renderDetailRows();
  document.getElementById('detailCatFilter').addEventListener('change', renderDetailRows);
  document.getElementById('detailSearch').addEventListener('input', renderDetailRows);
}

// --- Item Detail by Month — Volume & Spend (per-store) ---
let itemStoreMetric = 'amount';
let itemStoreSort = {key:'total', dir:-1};

function buildItemStoreFilterOptions(){
  const sel = document.getElementById('itemStoreCatFilter');
  const cats = ['All Categories', ...DATA.item_categories];
  sel.innerHTML = cats.map(c => `<option value="${c}">${c}</option>`).join('');
  sel.value = 'All Categories';
}

function buildItemStoreHead(){
  const row = document.getElementById('itemStoreHeadRow');
  const label = itemStoreMetric==='amount' ? 'Total Spend' : 'Total Qty';
  const cells = ['<th data-k="product">Product</th>', '<th data-k="category">Category</th>']
    .concat(DATA.months.map((m,i) => `<th class="num" data-k="m${i}">${m.split(' ')[0]}</th>`))
    .concat(['<th class="num" data-k="total" style="cursor:pointer;">' + label + ' ' + (itemStoreSort.key==='total' ? (itemStoreSort.dir<0?'▼':'▲') : '') + '</th>']);
  row.innerHTML = cells.join('');
  row.querySelectorAll('th[data-k]').forEach(th => th.addEventListener('click', () => {
    const k = th.dataset.k;
    if(itemStoreSort.key===k) itemStoreSort.dir *= -1; else itemStoreSort = {key:k, dir: k==='product'||k==='category' ? 1 : -1};
    buildItemStoreHead();
    renderItemStoreRows();
  }));
}

function renderItemStoreRows(){
  const view = currentView; // follows the location tabs at the top of the page: NETWORK / LU3 / LU5 / LU7
  const rows0 = DATA.item_store_matrix[view] || [];
  const catFilter = document.getElementById('itemStoreCatFilter').value;
  const q = document.getElementById('itemStoreSearch').value.trim().toLowerCase();
  let rows = rows0.filter(it =>
    (catFilter==='All Categories' || it.category===catFilter) &&
    (q==='' || it.product.toLowerCase().includes(q))
  );
  const k = itemStoreSort.key, dir = itemStoreSort.dir;
  const metricArr = itemStoreMetric==='amount' ? 'amount' : 'qty';
  const totalKey = itemStoreMetric==='amount' ? 'total_amount' : 'total_qty';
  rows = rows.slice().sort((a,b) => {
    let av, bv;
    if(k==='product' || k==='category'){ av=a[k]; bv=b[k]; return dir*av.localeCompare(bv); }
    else if(k==='total'){ av=a[totalKey]; bv=b[totalKey]; }
    else { const idx = parseInt(k.slice(1)); av = a[metricArr][idx]; bv = b[metricArr][idx]; }
    return dir*(av-bv);
  });
  document.getElementById('itemStoreCount').innerText = rows.length + ' of ' + rows0.length + ' items — ' + (view==='NETWORK'?'All Locations':view);
  const fmtCell = v => itemStoreMetric==='amount' ? fmtVND(v) : fmt(v);
  document.getElementById('itemStoreTable').innerHTML = rows.map(it => {
    const cells = it[metricArr].map(v => `<td class="num">${v===0 ? '<span style="color:#565d6b">—</span>' : fmtCell(v)}</td>`).join('');
    return `<tr><td>${it.product}</td><td>${it.category}</td>${cells}<td class="num">${fmtCell(it[totalKey])}</td></tr>`;
  }).join('');
}

function buildItemStoreTable(){
  buildItemStoreHead();
  renderItemStoreRows();
}

document.querySelectorAll('#itemStoreMetricTabs .subtab').forEach(t => t.addEventListener('click', () => {
  document.querySelectorAll('#itemStoreMetricTabs .subtab').forEach(x=>x.classList.remove('active'));
  t.classList.add('active');
  itemStoreMetric = t.dataset.m;
  itemStoreSort = {key:'total', dir:-1};
  buildItemStoreTable();
}));

function render(){
  buildTabs();
  buildKpis();
  buildTrendChart();
  buildCatChart();
  buildItemStoreTable(); // re-render on every store-tab switch, since it follows currentView
}

document.querySelectorAll('#priceTabs .subtab').forEach(t => t.addEventListener('click', () => {
  document.querySelectorAll('#priceTabs .subtab').forEach(x=>x.classList.remove('active'));
  t.classList.add('active');
  document.querySelectorAll('.pricePanel').forEach(p=>p.style.display='none');
  document.getElementById('panel-'+t.dataset.p).style.display='block';
}));

buildInsights();
buildItemStoreFilterOptions();
document.getElementById('itemStoreCatFilter').addEventListener('change', renderItemStoreRows);
document.getElementById('itemStoreSearch').addEventListener('input', renderItemStoreRows);
render();
buildCatIndexChart();
buildCatSpendChart();
buildImpactCharts();
buildCatImpactChart();
buildSupplierTable();
buildPctTable();
buildItemDetailTable();
</script>
</body>
</html>
```

Note the two `.subtab` click-handler blocks near the end are deliberately scoped by
container ID (`#itemStoreMetricTabs .subtab` and `#priceTabs .subtab`), not a bare
`.subtab` selector. They share the same CSS class for visual consistency, but a single
unscoped handler would deactivate the wrong tab group and try to open a
`panel-undefined` element when the item-store metric toggle is clicked. If you add
another `.subtab`-styled control in the future, give its click handler the same
ID-scoped treatment.

## Step 5 — Verify before shipping

The template above is already tested — you don't need to re-verify it on a routine
monthly refresh where only the source data changed. **Do** re-verify if you (or the
user) ask to modify the HTML/JS template itself:

1. Extract the `<script>...</script>` block and run `node --check` on it — catches
   syntax errors for free.
2. Run it inside a minimal hand-rolled DOM stub in Node (a real headless browser
   like jsdom/puppeteer is often unavailable or hangs in sandboxed environments —
   don't burn time fighting it; a stub with `getElementById`/`innerHTML`/
   `addEventListener` covers everything this dashboard's JS touches) and confirm it
   executes without throwing, and that computed KPI numbers match an independent
   Python calculation of the same totals. When testing via `eval()`, remember that
   `const`/`let` declared inside the eval'd script do NOT leak into the outer test
   scope in Node — append exposure lines to the *same eval'd string* itself, e.g.
   `global.__setCurrentView = function(v){ currentView = v; render(); };`, so the
   returned function closes over the real binding instead of a disconnected outer
   variable. This is essential for testing anything that depends on `currentView` or
   `itemStoreMetric`, since both are `let` declarations the dashboard mutates via
   click handlers.
3. Sanity-check the printed totals from Step 4 against a quick independent sum (e.g.
   `sum(r["amount"] for r in records if r["loc"]=="LU3")` for one month) before
   trusting the dashboard. For the category rollup specifically, confirm
   `sum(cat_impact impacts) == sum(this_month_impact impacts)` (up to rounding) —
   if they diverge by more than a few VND, an item is being counted in the wrong
   category or dropped from one of the two loops. For the item volume/spend table,
   confirm `sum(item_store_matrix["NETWORK"] total_amount)` equals the sum of the
   three per-location totals, which should also equal the network total from Step 2.

After writing the file, share it with the user and give a short read of what the
`buildInsights()` callout actually found — don't just hand over the file. Call out
anything that looks like a real anomaly (a location spend spike, a supplier's price
creeping up, a category basket getting too thin to trust) rather than reciting numbers
back.

## Common issues

| Symptom | Cause | Fix |
|---|---|---|
| Group-wide spend looks too high / doesn't match expectations | Internal transfer rows counted as real purchases | Confirm the `":" in contractor` filter is applied — see Step 1 |
| LU4 shows up trending to zero instead of being absent | LU4 not excluded | Filter locations to `LU3\|LU5\|LU7` only in the regex |
| A "cost increase" bar shows `delta = 0` in its tooltip | Using a cumulative/period-long impact metric instead of this-month | Recompute per Step 3a — one number per item, tied to the latest month only |
| Category price index looks suspiciously flat for Meat/Seafood/Cold Cut | Base month basket has very few SKUs for that category | Expected — dashed line + `n_skus` caveat is intentional, don't remove it |
| Price impact by category total doesn't match the item-level bars | Item-level charts (3a) only show the top/bottom 15 items, but the category rollup sums over ALL items | Expected — the category chart is complete, the item charts are a top-15 excerpt. They tell complementary stories, not the same story at different granularity |
| Item Detail by Month table looks empty / has fewer rows after switching store tabs | A store legitimately doesn't buy every item (different menu, different suppliers) | Expected, not a bug — row counts should differ per location (see Step 3f note); only zero-total items are omitted |
| Clicking the item-store Amount/Quantity toggle deactivates the Price Change subtabs (or vice versa) | The two `.subtab` groups' click handlers weren't scoped by container ID | Make sure both handlers use `#itemStoreMetricTabs .subtab` / `#priceTabs .subtab`, never a bare `.subtab` selector |
| `qty × price != amount` for some rows | Data format changed upstream (e.g. VAT now broken out separately) | Stop and investigate before trusting downstream numbers — this has held for every file so far |
| Chart doesn't update when switching location tabs | Chart.js instance not destroyed before recreating | Always go through `makeChart()`, never call `new Chart()` directly |
| Dashboard header still says last time's date range | Static text instead of `DATA.months[0]`/`[-1]` | The template already derives this dynamically in `buildInsights()` — don't hardcode date ranges anywhere else either |
