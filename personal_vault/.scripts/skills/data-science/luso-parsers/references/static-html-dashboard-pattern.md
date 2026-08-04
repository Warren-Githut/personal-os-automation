# Static HTML Dashboard from Parsed Data

## Pattern Overview
Generate interactive static HTML dashboards (Chart.js, no server) from parsed operational data. The HTML is a standalone file — open in browser, works offline.

## When to Use
- Warren wants to "see" data visually (trends, comparisons, breakdowns)
- The data has been parsed into structured format (dicts, lists)
- The consumer is Warren (non-IT) — open file = instant viz
- Data updates monthly/weekly — generate once per cycle

## Implementation Pattern (3 phases)

### Phase 1: HTML Template
Write a standalone HTML template with:
- **Chart.js CDN** (`<script src="https://cdn.jsdelivr.net/npm/chart.js">`)
- **CSS variables** for theme (light/muted/ink/accent)
- **KPI cards** grid (Revenue, COGS, WO%, etc.)
- **Store filter buttons** (ALL / LU3 / LU5 / LU7) — use CSS `.on` class
- **Chart canvases** with unique IDs (c1, c2, etc.)
- **Data table** sections (write-off/recon table, top items)

### Phase 2: Data Injection
The Python generator:
1. Builds the JavaScript data object
2. Injects JSON via `.replace()` on a static template (NOT f-string — avoids JS `${}` conflict)
3. Writes the complete HTML file

### Phase 3: Chart Rendering
- `renderAll()` = unified render (KPI + charts). Destroy old chart instances first.
- Store filter: click handler toggles `.on` class + calls `renderAll(store)`.
- Each chart uses a `makeChart(id, config)` helper that pushes to `chartInstances[]`.

## Pitfalls

- **Chart.js store data scope bug:** When building per-store datasets, always use `w[storeName][key]` (not `w.sys[key]`) for store-specific data. `w.sys[key]` only for the System dataset. Verify LU3 != LU5 != LU7 values before rendering.
- **Chart instance destruction:** `Chart.instances.forEach()` is NOT a valid API. Store instances in an array (`chartInstances.push(chart)`) and destroy via `chartInstances.forEach(c => c.destroy())`.
- **JS variable scope in chart generators:** Helper functions defined at module level cannot access local variables from calling functions. Pass all data (`weeks`, `labels`) as parameters explicitly.
- **Store filter full re-render:** Always destroy ALL charts before re-creating on filter change. Partial DOM updates leave stale Chart.js event listeners.
- **GSheets CSV export for standalone scripts:** Use `csv.DictReader` + `urllib.request` for standalones that need no PYTHONPATH. The COL dashboard generator (`gen_col_dashboard.py`) uses this pattern.

## Reference Implementations

| Dashboard | Script | Data Source | Charts |
|-----------|--------|-------------|--------|
| COGS Dashboard | `wastage_parse_gen.py` (--gen-html) | GSheet Data tab via fetch_sheets_api() | Revenue vs COGS bar, Food vs Bev stacked |
| Wastage Dashboard | `wastage_parse_gen.py` (--gen-html) | GSheet Data tab | WO/SH stacked bar, Category donut |
| GrabFood Trend | `gen_grabfood_dashboard.py` | `06_GrabFood_Weekly_Log.md` JSON blocks | 6 charts: Orders, GMV, Net, Ad Spend, Comm%, Mix |
| **COL Trend** | **`gen_col_dashboard.py`** | **GSheet CSV export (zero setup)** | **COL% line, Pass Rate bar, SPLH line. Threshold lines, store filter, green theme** |
