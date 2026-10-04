# COL Dashboard Generation Patterns (2026-07-06)

## Overview
Patterns discovered while building `gen_col_dashboard.py` — an HTML dashboard generator for COL (Cost of Labour) weekly data.

## Architecture: Standalone Generator (Not Parser-Dependent)
Unlike parsers that read GSheet → write vault markdown, the dashboard generator:
1. Fetches raw data DIRECTLY from GSheet (CSV export)
2. Aggregates historically (all weeks, not just current)
3. Outputs static HTML with Chart.js
4. No dependency on vault markdown format

This avoids the "parser first, then dashboard" dependency chain.

## Data Pipeline: GSheet CSV → Weekly Aggregation
```python
# Fetch all rows (381 rows, Mar-Jul 2026)
url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}"
rows = csv.DictReader(io.StringIO(urllib.request.urlopen(req).read().decode("utf-8-sig")))

# Group by ISO week, compute per-store + system aggregates
weeks = {}  # key = "2026-W27"
for r in rows:
    wid = iso_week(int(r["Date"]))
    weeks[wid][store] = accumulate(rev, hours, wages, status)
```

## Key Pattern: `getDataset()` Must NOT Use `isAll` to Select Data Source
**The single biggest bug in this session.** A shared helper that fetches store data AND system data must NEVER use the `isAll` view-mode flag to choose the data source:

```javascript
// WRONG — isAll collapses all stores to system line
function getDataset(key, storeName) {
    const data = weeks.map(w => isAll ? w.sys[key] : w[storeName][key]);
    // When isAll=true AND storeName='LU3', returns w.sys[key] NOT w['LU3'][key]
}
```

**Fix:** Always read `w[storeName][key]` for stores, `w.sys[key]` only for System. `isAll` only controls which datasets are IN THE CHART:

```javascript
const activeStores = isAll ? ['LU3','LU5','LU7','Sys'] : [store];
const datasets = activeStores.map(s => ({
    label: s,
    data: weeks.map(w => s === 'Sys' ? w.sys.col : w[s].col)
}));
```

## Key Pattern: Chart Instance Lifecycle
`Chart.instances.forEach(c => c.destroy())` is NOT valid Chart.js API. Track instances manually:

```javascript
let chartInstances = [];
function makeChart(id, config) {
    const chart = new Chart(document.getElementById(id), config);
    chartInstances.push(chart);
    return chart;
}
function destroyCharts() {
    chartInstances.forEach(c => { try { c.destroy(); } catch(e) {} });
    chartInstances = [];
}
```

## Color Theme for Multi-Store Dashboards
| Entity | Color | Hex | Usage |
|--------|-------|-----|-------|
| LU3 | Light green | `#CCFF99` | Line/bar, lighter for low values |
| LU5 | Medium green | `#4CAF50` | Line/bar, medium prominence |
| LU7 | Dark green | `#1B5E20` | Line/bar, high contrast |
| System | Blue | `#2196F3` | Bold, dashed, wider line |
| Background | Pale green | `#E8F5E9` | Page background |

## Verification Checklist
- [ ] Each store series has DISTINCT values (none equal to system mean)
- [ ] Chart instance array properly cleared on re-render
- [ ] Template placeholders all substituted (no `{PLACEHOLDER}` in output)
- [ ] CDN URLs use `cdn.jsdelivr.net/npm/chart.js` (not a specific version)
- [ ] Filter buttons toggle `.on` class correctly
- [ ] Data injection uses `.replace()` not f-strings (avoids JS `${}` conflict)
