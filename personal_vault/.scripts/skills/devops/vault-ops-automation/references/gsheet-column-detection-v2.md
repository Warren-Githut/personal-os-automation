# Refined GSheet Column Detection Patterns

**Refined patterns discovered during LTO, Item Sales, Hourly Cover parser builds.**

---

## 1. Outlet/Store Column Detection

**Problem**: GSheet column label is `"history_11_Item_Sales_Weekly_Log_Star_Horse Period: from 6/1/2026 to 6/7/2026 Outlet"` — not simple "Outlet" or "Store"

**Solution**: Search for "outlet" or "store" in label (case-insensitive), NOT exact match.

```python
ci_outlet = None
for i, col in enumerate(cols):
    label = (col.get("label") or "").strip().lower()
    if "outlet" in label or "store" in label:
        ci_outlet = i
        break

if ci_outlet is None:
    ci_outlet = 0  # fallback to first column
```

**Fallback**: Column 0 if no match.

---

## 2. Date Column Detection

**Problem**: LTO tab has label `"L'Usine - LTO Feedback Daily Log All dropdowns linked to _Lists | Date format: yyyy-mm-dd Date"`

**Solution**: Search for "date" in label.

```python
ci_date = None
for i, col in enumerate(cols):
    label = (col.get("label") or "").strip().lower()
    if label == "date" or "date" in label:
        ci_date = i
        break

if ci_date is None:
    ci_date = 0  # fallback
```

---

## 3. Fuzzy Store Name Matching

**GSheet store names**: `LU3-LTT-Q1`, `LU5-CM-Q7`, `LU7-SC-Q1`
**Internal codes**: `LU3`, `LU5`, `LU7`

**Solution**: Prefix match by `LU3`, `LU5`, `LU7` prefix.

```python
STORES = ["LU3-LTT-Q1", "LU5-CM-Q7", "LU7-SC-Q1"]
STORE_NORMALIZE = {
    "LU3-LTT-Q1": "LU3",
    "LU5-CM-Q7": "LU5",
    "LU7-SC-Q1": "LU7",
}

# In filter:
store_raw = gviz_cell(row, ci_store)
if store_raw and (store_raw.startswith("LU3") or store_raw.startswith("LU5") or store_raw.startswith("LU7")):
    result.append(row)

# In parse_row:
"store": STORE_NORMALIZE.get(store_raw, store_raw),
```

---

## 4. Pivot Table Column Position Mapping

**Hourly Cover tab**: Fixed column positions (store×hour rows, daily covers/revenue cols)

```python
# Day columns by position (covers at 3,5, revenue at 5,7, then +3 per day)
day_names = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
covers_idx = 3
for i, day in enumerate(day_names):
    day_cols[day] = {"covers": covers_idx, "revenue": covers_idx + 2}
    covers_idx += 3  # next day's covers is 3 cols later
```

**Fallback**: Also detect by header text for robustness.

```python
day_pattern = re.compile(r"(monday|tuesday|wednesday|thursday|friday|saturday|sunday)", re.I)
for i, col in enumerate(cols):
    if i in [3, 6, 8, 11, 13, 15, 17]: continue  # already mapped
    label = (col.get("label") or "").strip()
    m = day_pattern.search(label)
    if m:
        day = m.group(1).lower()[:3]
        if "guest" in label.lower() or "cover" in label.lower() or "khách" in label.lower():
            if day in day_cols: day_cols[day]["covers"] = i
        elif "sales" in label.lower() or "revenue" in label.lower() or "doanh" in label.lower() or "gross" in label.lower() or "vnd" in label.lower():
            if day in day_cols: day_cols[day]["revenue"] = i
```

---

## 5. Dynamic Header Row Detection

**COGS sheet**: Form header rows at top (rows 0-3), actual column headers at row 1.

```python
def find_header_row(rows):
    for i, row in enumerate(rows[:20]):
        cells = row.get("c", [])
        if len(cells) < 5: continue
        values = []
        for cell in cells[:13]:
            v = cell.get("v") if cell else None
            if v is not None:
                values.append(str(v).strip().lower())
        has_item = any("item" in v or "dish" in v for v in values)
        has_supplier = any("supplier" in v or "vendor" in v or "ncc" in v for v in values)
        if has_item and has_supplier:
            return i
    return 0
```

---

## 5. GSheet Store Name Normalization Map

```python
STORES = ["LU3-LTT-Q1", "LU5-CM-Q7", "LU7-SC-Q1"]
STORE_NORMALIZE = {
    "LU3-LTT-Q1": "LU3",
    "LU5-CM-Q7": "LU5",
    "LU7-SC-Q1": "LU7",
}
# In filter: match by prefix
store_raw = gviz_cell(row, ci_store)
if store_raw and (store_raw.startswith("LU3") or store_raw.startswith("LU5") or store_raw.startswith("LU7")):
    result.append(row)
# In parse_row:
"store": STORE_NORMALIZE.get(store_raw, store_raw),
```

---

## 6. Exact vs Partial Column Label Matching

```python
# Exact/strong matches first
if label == "outlet" or "outlet" in label:
    ci_outlet = idx
elif label == "supplier" or label == "vendor":
    ci_supplier = idx
# Fallback for partial matches if not set
elif "outlet" in label and ci_outlet is None:
    ci_outlet = idx
```

---

## 6. Parser Run Command (Standard)

```bash
LUSINE_HEADLESS=1 PYTHONPATH="C:/Users/khoans/Documents/Warren_OS_Local/vault/10_OPERATION_DATA/scripts/modules" python "../../../10_OPERATION_DATA/parsers/<parser_name>.py"
```