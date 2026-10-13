#!/usr/bin/env python3
"""
Purchasing Dashboard generator for L-Concepts (LU3, LU5, LU7).
Based on ops-purchasing-dashboard/SKILL.md.
Run with real Excel files in DATA_FOLDER, or use --sample to generate demo HTML.
"""

import os, re, glob, json, argparse, datetime
from collections import defaultdict
from openpyxl import load_workbook

# === Settings (edit paths as needed) ===
DATA_FOLDER = r"C:\Users\Pham Thi Kim Loan\Desktop\Claude\Purchasing\Data"
OUTPUT_FILE = r"C:\Users\Pham Thi Kim Loan\Desktop\Claude\Purchasing\Purchasing_Dashboard.html"

def load_all_records(data_folder):
    records = []
    for filepath in sorted(glob.glob(os.path.join(data_folder, "*.xlsx"))):
        fname = os.path.basename(filepath)
        m = re.match(r"(\d{4})\.(\d{2})\.xlsx", fname)
        if not m:
            continue
        month_key = f"{m.group(1)}.{m.group(2)}"
        wb = load_workbook(filepath, data_only=True)
        ws = wb[wb.sheetnames[0]]
        for row in ws.iter_rows(min_row=4, values_only=True):
            if row[0] is None and row[1] is None:
                continue
            if row[3] != "Purchase invoice":
                continue
            doc_num = str(row[1] or "")
            loc_m = re.match(r"(LU3|LU5|LU7)", doc_num)
            if not loc_m:
                continue
            contractor = str(row[17] or "")
            if ":" in contractor:
                continue
            records.append({
                "month": month_key, "loc": loc_m.group(1),
                "sku": row[4], "product": row[5],
                "qty": row[6] or 0, "price": row[7] or 0,
                "category": row[12] or "Uncategorized",
                "amount": row[27] or 0, "contractor": contractor,
            })
    return records

def build_dashboard(records, output_file):
    MONTHS = sorted(set(r["month"] for r in records))
    def month_label(m):
        return datetime.datetime(int(m[:4]), int(m[5:7]), 1).strftime("%b %Y")
    MONTH_LABELS = {m: month_label(m) for m in MONTHS}
    LOCS = ["LU3", "LU5", "LU7"]

    # Step 2 aggregates
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

    # Price series
    prod_month = defaultdict(lambda: defaultdict(lambda: {"qty": 0.0, "amount": 0.0}))
    prod_name, prod_cat, prod_total_spend = {}, {}, defaultdict(float)
    for r in records:
        key = (r["sku"], r["product"])
        prod_month[key][r["month"]]["qty"] += r["qty"]
        prod_month[key][r["month"]]["amount"] += r["amount"]
        prod_name[key] = r["product"]
        prod_cat[key] = r["category"]
        prod_total_spend[key] += r["amount"]

    # 3a this-month impact
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
            continue
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

    # 3b Laspeyres
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

    # 3c supplier creep
    supplier_prod_month = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: {"qty": 0.0, "amount": 0.0})))
    supplier_total = defaultdict(float)
    for r in records:
        key = (r["sku"], r["product"])
        supplier_prod_month[r["contractor"]][key][r["month"]]["qty"] += r["qty"]
        supplier_prod_month[r["contractor"]][key][r["month"]]["amount"] += r["amount"]
        supplier_total[r["contractor"]] += r["amount"]

    supplier_creep = []
    for s, prods in supplier_prod_month.items():
        if supplier_total[s] < 5_000_000:
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
        if weight_sum > 0 and n_products >= 2:
            supplier_creep.append({"supplier": s, "pct": round(weighted_sum / weight_sum, 1),
                                    "total_spend": round(supplier_total[s]), "n_products": n_products})
    supplier_creep = sorted(supplier_creep, key=lambda x: -abs(x["pct"]))[:20]

    # 3d % movers
    pct_movers = []
    prod_price_series = {}
    for key, months in prod_month.items():
        series = {m: months[m]["amount"] / months[m]["qty"] for m in MONTHS if m in months and months[m]["qty"] > 0}
        prod_price_series[key] = series
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

    # 3e item matrix
    item_matrix = []
    for key, series in prod_price_series.items():
        prices = [round(series[m]) if m in series else None for m in MONTHS]
        item_matrix.append({"product": prod_name[key], "category": prod_cat[key] or "Uncategorized",
                             "prices": prices, "total_spend": round(prod_total_spend[key])})
    item_matrix.sort(key=lambda x: -x["total_spend"])
    item_categories = sorted(set(it["category"] for it in item_matrix))

    # 3f item store
    loc_prod_month = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: {"qty": 0.0, "amount": 0.0})))
    for r in records:
        key = (r["sku"], r["product"])
        loc_prod_month[r["loc"]][key][r["month"]]["qty"] += r["qty"]
        loc_prod_month[r["loc"]][key][r["month"]]["amount"] += r["amount"]

    def build_item_store_rows(loc_filter=None):
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
                continue
            rows.append({"product": prod_name[key], "category": prod_cat[key] or "Uncategorized",
                         "qty": qty_series, "amount": amt_series,
                         "total_qty": total_qty, "total_amount": total_amt})
        rows.sort(key=lambda x: -x["total_amount"])
        return rows

    item_store_matrix = {"NETWORK": build_item_store_rows(None)}
    for loc in LOCS:
        item_store_matrix[loc] = build_item_store_rows(loc)

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

    # NOTE: Full HTML templates are embedded in SKILL.md.
    # This script is a runnable skeleton. For complete HTML, extract templates from SKILL.md
    # or keep the local generator that includes HTML_TEMPLATE_BEFORE / AFTER.
    html = "<!-- Full HTML template lives in SKILL.md. This is the data payload. -->\n"
    html += "<script>const DATA = " + DATA_JSON + ";</script>\n"
    html += "<!-- Paste the rest of the dashboard HTML/JS from SKILL.md here for a complete file. -->\n"

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Wrote {output_file} — {len(html):,} chars, {len(MONTHS)} months, {len(item_matrix)} items, "
          f"₫{sum(network_monthly):,} total network spend.")
    print("NOTE: This output is data-only. Embed HTML templates from SKILL.md for the full interactive dashboard.")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample", action="store_true", help="Generate with sample data (not implemented in this push)")
    parser.add_argument("--data-folder", default=DATA_FOLDER)
    parser.add_argument("--output", default=OUTPUT_FILE)
    args = parser.parse_args()

    if args.sample:
        print("Sample mode: use the local artifacts/generate_purchasing_dashboard.py for full demo HTML.")
        return

    records = load_all_records(args.data_folder)
    print(f"Loaded {len(records)} external purchase records.")
    build_dashboard(records, args.output)

if __name__ == "__main__":
    main()
