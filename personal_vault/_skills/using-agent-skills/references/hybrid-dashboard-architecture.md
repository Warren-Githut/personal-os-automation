# Hybrid Dashboard Architecture

## Overview

Reusable pattern for structuring operational HTML dashboards alongside vault data. Solves the tension between "centralize all dashboards in one place" (hard to maintain, loses data context) and "scatter dashboards everywhere" (impossible to find).

## Architecture

```
30_KNOWLEDGE_BASE/wiki/
├── 00_DASHBOARDS.md              ← Centralized INDEX (1 file to rule them all)
├── 06_lusine_operations/
│   ├── GrabFood_Rolling_Tracker.md
│   └── GrabFood_Trend_Dashboard.html   ← Distributed: lives next to its data context
├── 08_menu_cogs/
│   ├── COGS_Dashboard_2026-06.html     ← Distributed
│   ├── Wastage_Dashboard_2026-06.html  ← Distributed
│   └── DASHBOARDS.md                   ← Sub-index (optional, for folder with 2+ dashboards)
└── 04_labour_costs/                    ← Future: COL_Dashboard.html here
```

## Pattern Rules

| Rule | Why |
|------|-----|
| **1. Centralized index** | `wiki/00_DASHBOARDS.md` — one table with every dashboard: name, path, data scope, last refresh |
| **2. Distributed files** | Each `.html` lives in the wiki subfolder closest to its data domain and analysis pages. Cross-domain dashboards (e.g. Item Sales) go in `wiki/dashboards/`. |
| **3. Sub-index optional** | If a folder has 2+ dashboards (e.g. COGS + Wastage), add a `DASHBOARDS.md` in that folder too |
| **4. Tech: self-contained HTML** | Chart.js CDN, no server needed. Data embedded in JS object (NOT fetched at runtime — `file://` blocks CORS). `File → Open` works in any browser. |
| **5. Data source** | Each dashboard reads from the vault's `_accumulation/{domain}.json` (updated by parser each run). DATA MUST BE EMBEDDED in the HTML's JS (e.g. `const DATA = {...}`) at build time, not fetched. |
| **6. Naming convention** | `{Domain}_Dashboard_{period}.html` — grep-able, sortable by period or by domain |
| **7. Auto-rebuild** | Parser writes markdown + accumulation JSON → builder script (standalone `.py`) rebuilds self-contained HTML. Trigger via cron +5 min after parser. Or manual via `python build_*_dashboard_data.py`. |
| **8. Link in weekly report** | Absolute path (`file:///C:/path/to/dashboard.html`) written into the weekly markdown entry so Warren clicks/copies into browser — non-friction. |
| **9. Color scheme (L'Usine)** | LU3: `#CCFF99`, LU5: `#4CAF50`, LU7: `#1B5E20`, System: `#2196F3`, BG: `#E8F5E9`. |
| **10. PDF export** | Include html2canvas + jsPDF CDN. Add export button that captures full dashboard content and saves as A4 PDF. |
```markdown
# DASHBOARDS — Central Index

| Dashboard | File | Data Scope | Last Refresh | Nguồn Data |
|-----------|------|------------|-------------|------------|
| GrabFood Trend | [[06_lusine_operations/GrabFood_Trend_Dashboard.html]] | W18-W26 (Apr-Jun 2026) | Pending | `06_GrabFood_Weekly_Log.md` |
| COGS Dashboard | [[08_menu_cogs/COGS_Dashboard_2026-06.html]] | Jun 2026 | 2026-07-05 | `03_COGS_Supplier_Monthly_Log.md` |
```

## When to Use

- Warren asks for a dashboard
- You're reviewing data architecture and notice dashboard sprawl
- Adding a new automated report that could benefit from visual trend display
