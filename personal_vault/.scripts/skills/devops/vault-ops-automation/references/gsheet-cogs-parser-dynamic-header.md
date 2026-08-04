# COGS Parser: Dynamic Header Row Detection

## Problem
The PRICE_CHANGE tab in LU_COL_ENGINE_V4 has variable form/header rows at the top (form title, document code, requester, department, note). The actual data header row (Item, Supplier, Unit, Price Old, Price New, % Change, Volume) appears at a variable row index.

## Solution: Dynamic Header Detection

```python
def find_header_row(rows):
    """Find the row that contains actual column headers (Item, Supplier, Unit, etc.)."""
    for i, row in enumerate(rows[:20]):  # scan first 20 rows
        cells = row.get("c", [])
        if len(cells) < 5:
            continue
        values = []
        for cell in cells[:13]:
            v = cell.get("v") if cell else None
            if v is not None:
                values.append(str(v).strip().lower())
        has_item = any("item" in v or "dish" in v for v in values)
        has_supplier = any("supplier" in v or "vendor" in v or "ncc" in v for v in values)
        if has_item and has_supplier:
            print(f"🔍 Found header row at index {i}")
            return i
    print("⚠️  Could not auto-detect header row, using first data row")
    return 0
```

## Column Mapping from Header Labels

```python
def build_column_map(header_cells):
    label_to_idx = {}
    for i, cell in enumerate(header_cells[:13]):
        if cell and cell.get("v"):
            label = str(cell["v"]).strip().lower()
            label_to_idx[label] = i
    return label_to_idx

# Map by exact/strong matches first, then fallback
for label, idx in label_to_idx.items():
    if label in ("item", "items", "items description", "items descriptions", "dish", "món"):
        ci_item = idx
    elif label in ("supplier", "vendor", "ncc", "nhà cung cấp"):
        ci_supplier = idx
    # ... etc with fallbacks
```

## Column Detection Debugging

Always print detected columns:
```python
print(f"🔍 COGS header labels: {list(label_to_idx.keys())[:10]}")
print(f"   Item={ci_item}, Supplier={ci_supplier}, Unit={ci_unit}, PriceOld={ci_price_old}, PriceNew={ci_price_new}, Pct={ci_pct}, Volume={ci_volume}")
```