# GSheet Merged Cells — Forward-Fill Pattern

## Problem

Google Sheets often uses **merged cells** (or visual grouping) where a category label appears only once at the top of a group, and subsequent rows leave the cell empty. This is common in exported pivot tables and manually formatted sheets.

Example — "Item group" column:
```
| Item group        | Item                         |
|-------------------|------------------------------|
| All-day Breakfast | Avocado Toast 4.0           |
| (empty)           | Chilli Prawn Scrambled Eggs |
| (empty)           | Classic Bacon Eggs Benedict |
| All-day Breakfast Total | 221                    |
| Asian Dishes      | Com Tam Broken Rice 3.0     |
| (empty)           | L'Usine Chicken Rice        |
| Asian Dishes Total | 44                         |
```

The parser must **forward-fill** the `item_group` value from the last non-empty cell, and **skip "Total" rows**.

## Implementation Pattern

### 1. Track current value + detect Total rows

```python
current_item_group = ""
for row in rows:
    # Detect Total rows FIRST (before forward-fill)
    item_name = get(row, ci_item) or ""
    if "Total" in item_name:
        continue  # Skip "All-day Breakfast Total", "Asian Dishes Total", etc.

    # Forward-fill: update when cell has value, else inherit
    cell_value = get(row, ci_item_group) or ""
    if cell_value:
        current_item_group = cell_value
    item_group = current_item_group
```

### 2. Two-stage fill pattern

The same pattern applies to store names (Outlet column):

```python
current_store = None
for row in rows:
    store_raw = get(row, ci_outlet)
    if store_raw:
        current_store = store_raw
    elif current_store is None:
        continue  # No data before first outlet header
```

### 3. Combined: Store forward-fill + Item Group forward-fill + Total skip

```python
current_store = None
current_item_group = ""
for row in rows:
    # Store forward-fill
    store_raw = get(row, ci_outlet)
    if store_raw:
        current_store = store_raw
    elif current_store is None:
        continue

    # Skip Total rows (e.g. "All-day Breakfast Total", "Grand Total")
    item_name = get(row, ci_item) or ""
    if "Total" in item_name:
        continue

    # Skip system-level Grand Total names
    if current_store and "Grand" in current_store:
        continue

    if current_store not in STORES_GSHEET:
        continue

    # Item Group forward-fill
    cell_value = get(row, ci_item_group) or ""
    if cell_value:
        current_item_group = cell_value
    item_group = current_item_group
```

## Common Pitfalls

| Pitfall | Symptom | Fix |
|---------|---------|-----|
| **Skipping Total rows too late** | Total rows counted as data items | Check "Total" in item_name **before** forward-fill logic |
| **Forward-fill from wrong column** | Items get wrong group name | Verify column indices match GSheet layout |
| **Grand Total vs group Total** | System totals leak into data | Check both "Total" in item_name AND "Grand" in store_name |
| **Empty cells after forward-fill** | Items show blank/"—" in output | Verify the column actually has a header row with value; some GSheet tabs don't use merged cells but leave cells genuinely blank |
| **Forward-fill across store boundaries** | Item from store B gets store A's group | Reset `current_item_group = ""` when `store_raw` changes |

## Testing

After implementing forward-fill, verify:
```bash
grep -c " — | " <output_log>.md  # Should be 0 if all groups resolved
grep "| — | " <output_log>.md     # Should show only genuinely ungrouped items
```

The Executive Summary's `Top group` should now show a real category name (e.g. "Coffee", "All-day Breakfast") instead of "Uncategorized".