# Broken-[[wikilink]] Audit + Safe Rewrite — Working Script (2026-07-20)

Reusable, copy-and-run. Adopted from the real Monday Vault Health Check that fixed 441 ghost
links + 12 dashboard links across 77 files in Warren's vault.

## 1. Classify (basename-resolved, dedup by unique target)

```python
import os, re, glob
VAULT = r"C:/Users/khoans/Documents/Warren_OS_Local/vault"
files = [f for f in glob.glob(VAULT + '/**/*.md', recursive=True) if '.git' not in f]
basemap = {}
for f in files:
    stem = os.path.splitext(os.path.basename(f))[0].lower()
    basemap.setdefault(stem, []).append(os.path.normpath(f))
htmls = set(os.path.normpath(p).lower() for p in glob.glob(VAULT+'/**/*.html', recursive=True) if '.git' not in p)
linkre = re.compile(r'\[\[([^\]\|#]+)')

targets = {}  # base -> set of raw link texts
for f in files:
    try: txt = open(f, encoding='utf-8', errors='ignore').read()
    except: continue
    for m in linkre.findall(txt):
        t = m.strip()
        if not t: continue
        base = re.sub(r'\.md$','', os.path.basename(t), flags=re.I).lower()
        targets.setdefault(base, set()).add(t)

# Classify each unique base
for base, raws in sorted(targets.items()):
    if base in basemap:                 print("OK     ", base)
    elif base.endswith('.html'):        print("HTML   ", base, "EXISTS" if any(h.endswith(base) for h in htmls) else "MISSING")
    elif base.endswith('.csv'):         print("CSV    ", base, "(ignore)")
    else:                               print("GONE   ", base)
```

## 2. Rewrite (dry-run first, then exec)

```python
from pathlib import Path
import os, re, glob
VAULT = Path(r"C:/Users/khoans/Documents/Warren_OS_Local/vault")
GONE = {  # exact basenames (lowercase, NO .md suffix) of truly-deleted/renamed files
 'col_breakdown','dinh_bien_framework_v3','lessons_learned','system_view','extra_hours_tracking_2026',
 'action_items','april_2026_bev_lto','breakeven_analysis','combined_food_bev_analysis',
 'covers_hourly_lu3_2026_rolling','covers_hourly_lu5_2026_rolling','covers_hourly_lu7_2026_rolling',
 'lu5_profitability_watch','lu5_reallocation','manpower_plan_analysis_tracking','menu_engineering',
 'monthly_p&l_template','pl_target_all_stores_2026-05-12','pl_variance_tracker_2026','post_lto_framework',
 'profit_loss_analysis','q1_2026_cogs_summary','q1_2026_consolidated_p&l','q1_2026_store_p&l',
 'rent_fixed_costs','rent_occupancy_cost','sop_005_context_form_template','staffing_breakeven_implications',
 'store_profiles','workflow_guide_nonit','02_hr_movements_month_analysis_rolling'}
HTML = {  # basename -> vault-relative path of the .html file
 '01_ssot_01_weekly_revenue_dashboard.html':'30_KNOWLEDGE_BASE/wiki/dashboards/01_SSOT_01_Weekly_Revenue_Dashboard.html',
 'col_trend_dashboard.html':'30_KNOWLEDGE_BASE/wiki/04_labour_costs/COL_Trend_Dashboard.html',
 'cph_dashboard.html':'30_KNOWLEDGE_BASE/wiki/04_labour_costs/CPH_Dashboard.html',
 'extra_hours_tracker.html':'30_KNOWLEDGE_BASE/wiki/04_labour_costs/Extra_Hours_Tracker.html',
 'grabfood_trend_dashboard.html':'30_KNOWLEDGE_BASE/wiki/06_lusine_operations/GrabFood_Trend_Dashboard.html',
 'oil_tracking_dashboard.html':'30_KNOWLEDGE_BASE/wiki/04_labour_costs/OIL_Tracking_Dashboard.html',
 'wastage_dashboard_2026-06.html':'30_KNOWLEDGE_BASE/wiki/08_menu_cogs/Wastage_Dashboard_2026-06.html',
 'hourly_cover_revenue_dashboard.html':'30_KNOWLEDGE_BASE/wiki/dashboards/hourly_cover_revenue_dashboard.html',
 'menu_gp_trend.html':'30_KNOWLEDGE_BASE/wiki/dashboards/menu_gp_trend.html'}

linkre = re.compile(r'\[\[([^\]\|#]+)(?:\|([^\]]+))?\]\]')
files = [Path(p) for p in glob.glob(str(VAULT/'**/*.md'), recursive=True) if '.git' not in p]
DRY = True  # set False to write
gone_n=html_n=changed=0
for fp in files:
    rel = str(fp.relative_to(VAULT)).replace('\\','/')
    if rel.startswith('_archives/memory') or rel.startswith('.archive'):
        continue
    try: txt = fp.read_text(encoding='utf-8', errors='ignore')
    except: continue
    new = txt
    for m in linkre.finditer(txt):
        t = m.group(1).strip(); alias = m.group(2)
        base = re.sub(r'\.md$','', os.path.basename(t), flags=re.I).lower()
        if base in GONE:
            new = new.replace(m.group(0), alias if alias else os.path.basename(t)); gone_n += 1
        elif base in HTML:
            url = 'file:///' + str((VAULT/HTML[base]).resolve()).replace('\\','/')
            label = alias if alias else os.path.basename(HTML[base])
            new = new.replace(m.group(0), f'[{label}]({url})'); html_n += 1
    if new != txt:
        if not DRY: fp.write_text(new, encoding='utf-8')
        changed += 1
print(f"DRY={DRY} files_changed={changed} gone={gone_n} html={html_n}")
```

## 3. Verify (re-run Pass-1 classifier on the result)
Re-run the classify script; expect 0 `GONE` remaining. Spot-check 2 converted files with
`grep -n 'file:///'`. Confirm `git status --short | wc -l` matches expected changed-file count.

## Notes from the real run
- 500 naive "broken" → 37 real GONE targets after basename resolution.
- 77 live files rewritten; 17 `_archives/memory/` snapshots correctly EXCLUDED.
- `search_files` returned stale/empty on Windows — used `terminal` `find`/`grep` for disk truth.
- Path-form links like `[[08_menu_cogs/Menu_Engineering.md]]` need `.md` stripped from `GONE`
  keys or they slip through (basename still matches).
