# Python → HTML Dashboard Generation

> **When to use:** You need to generate an interactive static HTML dashboard from Python data (e.g. daily/weekly ops data → Chart.js dashboard that Warren opens in browser).

## Core Pattern

```
Python data (dict/list) → json.dumps() → inject into HTML template via .replace() → static .html file
```

### Why .replace() instead of f-strings

**Problem:** JavaScript uses `${var}` template literals and CSS uses `{var}` syntax. Python f-strings interpret `{...}` and the `:` in JS ternaries (`condition ? a : b`) triggers f-string format-spec parsing.

**Fix option 1 — Single-brace placeholders:** Store the HTML as a regular (non-f-string) string with `{PLACEHOLDER}` markers. Use `.replace()` to inject JSON:

```python
HTML_TEMPLATE = """...var DATA = {DATA_JSON};..."""
html = HTML_TEMPLATE.replace("{DATA_JSON}", json.dumps(data))
```

**Fix option 2 — Double-underscore placeholders (preferred when CSS/HTML uses `{}`):** Use `__VAR__` as placeholders to avoid any conflict with CSS braces, JS objects, or HTML curly quotes:

```python
HTML_TEMPLATE = """...var DATA = __DATA_JSON__;..."""
# No `{{ }}` needed anywhere — the template uses only __VAR__ markup
placeholders = {
    "__DATA_JSON__": json.dumps(data),
    "__LABELS__": json.dumps(["W24","W25","W26"]),
}
html = HTML_TEMPLATE
for k, v in placeholders.items():
    html = html.replace(k, str(v))
```

This approach avoids all f-string escaping issues and prevents accidental brace matching with CSS `{}` or JS object literals `{}`.
var DATA = {DATA_JSON};
function fmt(n) {{
  return n < 0 ? "(" + Math.abs(n).toLocaleString() + ")" : Math.round(n).toLocaleString();
}}
</script>
</html>"""

# In the generator function:
def generate(data):
    import json
    return HTML_TEMPLATE.replace("{DATA_JSON}", json.dumps(data))
```

Note: Double braces `{{ }}` become single braces `{ }` in Python triple-quoted strings.

### Structure Components

| Component | What | Example |
|-----------|------|---------|
| **CSS** | Inline `<style>` (no external files) | `:root{--bg:#f6f7f9} body{...}` |
| **Chart.js** | CDN via `<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/...">` | No local install needed |
| **Data** | JSON embedded in `<script>` block | `var DATA = {DATA_JSON};` |
| **Charts** | `<canvas>` elements rendered by Chart.js | `new Chart(ctx, {type:'bar', data:...})` |
| **Tables** | Dynamically built from JS arrays | `rows.forEach(r => table += '<tr>' + ...)` |

### Chart.js Patterns (Static HTML)

- **Bar chart**: `type:'bar'` with multiple datasets (Revenue vs COGS)
- **Stacked bar**: `scales.x.stacked: true` (Food vs Beverage)
- **Doughnut**: `type:'doughnut'` for category breakdowns
- **Grouped store filter**: Re-render charts with different data per store
- **Tab switching**: Click handler changes `tab` variable → re-renders table

### Common Pitfalls

1. **f-string + JS `${}` conflict**: Use `.replace()` on non-f-strings. Never use f-strings for HTML that contains JS template literals or CSS.
2. **Data injection with commas in numbers**: Use `toLocaleString("en-US")` in JS, not Python formatting, for displayed numbers. Python injects via `json.dumps()` which produces raw numbers.
3. **Chart.js canvas not rendering**: Wrap in `<div class="chartbox" style="position:relative;height:260px">` — Chart.js needs explicit height.
4. **CDN failure**: The HTML won't load charts without internet. No fallback needed for ops dashboards (Warren always has internet).
5. **Data sign conventions**: Before injecting aggregated data into HTML tables, trace the sign convention through the full pipeline: raw data → parse → aggregate → display. Common mistake: mixing shortage (negative) and surplus (positive) in the same category table, or displaying shortage as a positive absolute value. Always separate opposite-signed metrics into distinct display groups (e.g. "Shortage by Category" table ≠ "Surplus by Category" table).
6. **json.dumps() injects its own braces**: The template uses `var DATA = {PLACEHOLDER};`. After `.replace("{PLACEHOLDER}", json.dumps(data))`, the result is `var DATA = {...};` — with one pair of braces from json.dumps. Do NOT add extra `{}` around the placeholder. If the page is blank when opened in browser, open DevTools console (F12) — the most likely cause is a JS syntax error from escaped braces or f-string artifacts.
7. **Store-level data must be computed per-store, not derived by dividing system totals**: When generating per-store KPI cards, aggregate the raw data filtered by store. Never use integer division (`system // 3`) for even split — this produces incorrect numbers and loses per-store variation.

### Verification

```python
html = generate(data)
assert "chart.js" in html       # Chart.js CDN present
assert "{{" not in html         # No f-string contamination (double open brace)
assert len(html) > 1000         # Non-trivial output
open("dashboard.html", "w").write(html)
# THEN OPEN IN BROWSER — code inspection alone does NOT detect JS runtime errors
# Visual check: KPI cards show numbers, charts render, store filter switches work
# Fix blank pages by checking browser DevTools Console (F12) for JS syntax errors
```
