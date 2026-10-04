# COGS → Recipe Cost Propagation

## Problem

Recipe_Index.json has baseline recipe costs per menu item. But ingredient prices change monthly (captured in COGS Supplier Log). To compute accurate GP%, recipe costs must be adjusted for current-month ingredient prices.

## Technique

### Step 1: Build Ingredient→Recipes Index

```python
from collections import defaultdict

ing_to_recipes = defaultdict(list)
for recipe in recipes:
    for ing in recipe.get("ingredients", []):
        ing_name = ing.get("name", "").strip()
        # Normalize: split on / to remove Vietnamese translation
        ing_norm = ing_name.split("/")[0].strip().lower()
        ing_to_recipes[ing_norm].append((recipe["item_name"], ing, recipe))
```

### Step 2: Parse COGS Supplier Log for Price Changes

```python
# Scan pipe-delimited rows for a column with +N% or -N%
# | # | Item Name | Supplier | UoM | Old | New | Δ% | Volume | Impact |
adjustments = {}
for line in section.split("\n"):
    if not line.startswith("|"):
        continue
    parts = [p.strip() for p in line.split("|")]
    for i, p in enumerate(parts):
        m = re.match(r'^([+-]?\d+(?:\.\d+)?)%$', p):
            item_name = parts[1].split("/")[0].strip().lower()
            adjustments[item_name] = float(m.group(1))
```

### Step 3: Apply Proportional Adjustment

```python
import copy
modified_lookup = copy.deepcopy(recipe_lookup)  # deep copy preserves originals

for ing_name, delta_pct in adjustments.items():
    if ing_name not in ing_to_recipes:
        continue
    for recipe_name, ing, recipe in ing_to_recipes[ing_name]:
        recipe_key = recipe_name.lower()
        ing_cost = ing.get("cost_vnd", 0)
        cost_delta = ing_cost * (delta_pct / 100.0)
        current = modified_lookup[recipe_key]
        new_cost = current["cost_total"] + cost_delta
        current["cost_total"] = round(new_cost)  # accumulates across multiple ingredients
```

### Step 4: Use Adjusted Costs in GP Calculation

```python
for item in matched:
    adjusted_cost = modified_lookup[item_key]["cost_total"]
    gp = net_rev - (qty * adjusted_cost)
    gp_pct = gp / net_rev * 100
```

## Pitfalls

| Issue | Fix |
|-------|-----|
| **Shallow copy** | `dict(original)` shares inner dicts → `copy.deepcopy()` preserves originals |
| **Vietnamese / bilingual names** | Both COGS and Recipe_Index use `English / Tiếng Việt` format. Always split on `/` and compare the English part |
| **Multiple ingredients per recipe** | Accumulate adjustments: each ingredient adds its delta to the running cost_total |
| **Only adjust, never overwrite** | The adjusted cost is ephemeral — used only in this month's GP calculation. Recipe_Index.json is NEVER rewritten |
| **Unit mismatch** | COGS log uses supplier units (kg, bottle). Recipe_Index uses per-portion cost (ing.cost_vnd). Skip UoM conversion — use cost_vnd directly from Recipe_Index as it's already per-portion |
