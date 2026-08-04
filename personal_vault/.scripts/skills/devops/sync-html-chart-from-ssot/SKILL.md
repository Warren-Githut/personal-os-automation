---
name: sync-html-chart-from-ssot
description: "Sync a Chart.js HTML dashboard from a markdown SSOT (rolling tracking file). Parse month blocks from the SSOT, rebuild the dashboard's <script> chart datasets, and MANDATORY node --check the generated JS before claiming done. Use when a static HTML chart must reflect new months/data in a vault SSOT without hand-editing."
type: skill
version: 1.0
status: active
applies_to: ["Hermes Desktop"]
---

# sync-html-chart-from-ssot — Auto-sync Chart.js dashboard from markdown SSOT

> Pattern for keeping a Chart.js HTML dashboard in sync with a vault **SSOT rolling tracking file** (markdown, newest-month-on-top block structure). Replaces hand-editing chart datasets every month.

## When to use
- A vault has a markdown SSOT (e.g. `aa_SSOT_Total_Working_Hours_Tracking_Rolling.md`) with per-month `## Month YYYY` blocks, and a companion `.html` Chart.js dashboard that should show all months.
- New month ingested → dashboard must update automatically (don't hand-edit `data:[...]` arrays).
- Any time you generate or rewrite an `.html` file containing inline `<script>` Chart.js code.

## The 4-Step Pattern

### Step 1 — Parse SSOT month blocks (newest-on-top)
```python
import re
from pathlib import Path
SSOT = Path("vault/30_KNOWLEDGE_BASE/wiki/04_labour_costs/aa_SSOT_Total_Working_Hours_Tracking_Rolling.md")
MON_VN = {"January":"Jan",...,"June":"Jun",...}

def parse_blocks(content):
    heads = list(re.finditer(r"^##\s+([A-Za-z]+)\s+(\d{4})\s*$", content, re.MULTILINE))
    blocks = []
    for i, h in enumerate(heads):
        name, yr = h.group(1), h.group(2)
        start = h.start()
        end = heads[i+1].start() if i+1 < len(heads) else len(content)
        blk = content[start:end]
        # Tổng Quan table row — ALLOW **bold** + optional * around cells
        row_re = re.compile(r"^\|\s*\**\s*(LU[357]|System)\s*\**\s*\|\s*\**\s*([\d,.]+)\s*\**\s*\|\s*\**\s*([\d,.]+)\s*\**\s*\|", re.MULTILINE)
        data = {}
        for rm in row_re.finditer(blk):
            s = rm.group(1)
            data[s] = {"total": float(rm.group(2).replace(",","")),
                       "ot":    float(rm.group(3).replace(",",""))}
        if "System" in data and any(k in data for k in ("LU3","LU5","LU7")):
            blocks.append((f"{name} {yr}", data))
    return blocks
```
KEY: the System row is `| **System** | **10,375.9** | ...` — your row regex MUST tolerate `**` (and the number cells too). A regex that expects bare `| System |` misses the bold row → block filtered out → silent data loss.

### Step 2 — Build chart dataset bodies
Generate the JS dataset arrays from `blocks`. Return the FULL chart body INCLUDING the closing `});`:
```python
def build_hours_trend(blocks):
    months = [MON_VN[b[0].split()[0][:3]] for b in blocks]  # ['Jun','May','Apr']
    def ser(key): return [round(blocks[i][1]["System"][key],2) for i in range(len(blocks))]
    datasets = [f"    {{ label:'System OT', data:[{','.join(str(x) for x in ser('ot'))}], ... }}"]
    return ("  data: { labels: months, datasets: [\n" + ",\n".join(datasets) + "\n  ]},\n"
            "  options: { ... }\n});")   # <-- MUST end with }); NOT just }
```
CRITICAL: the body string must end with `});` (close object + close `new Chart(` call). If you end with `}` only, the generated HTML has a syntax error and **ALL charts after it render blank** ("mất hết").

### Step 3 — Rewrite the HTML <script> (targeted, not whole-file)
Use `re.sub` on the specific chart block. Match from `new Chart(getElementById('X'), {` through its closing `});`, replace with `group(1) + "\n  type: 'line',\n" + body` (body already includes `});`, so do NOT append another `}`):
```python
def rewrite_script(html, months_js, hours_body, pay_body):
    html = re.sub(r"const months = \[[^\]]*\];", f"const months = {months_js};", html, count=1)
    html = re.sub(
        r"(new Chart\(document\.getElementById\('hoursTrend'\),\s*\{)(.*?)(\}\);)",
        lambda m: m.group(1) + "\n  type: 'line',\n" + hours_body,
        html, count=1, flags=re.DOTALL)
    # same for otPayTrend ...
    return html
```
PITFALL: if the HTML already has a stray `}` from a previous broken sync, `re.sub` with `count=1` only replaces the FIRST `new Chart` block and leaves the orphan `}` outside the match → it persists. After rewriting, assert zero stray single-brace lines (see Step 4).

### Step 4 — MANDATORY node --check gate (NEVER skip)
Extract `<script>...</script>` and run the real V8 parser:
```python
import re, subprocess, tempfile, os
h = open(HTML, encoding="utf-8").read()
js = re.search(r"<script>(.*)</script>", h, re.DOTALL).group(1)
fd, p = tempfile.mkstemp(suffix=".js"); os.close(fd)
open(p,"w").write(js)
r = subprocess.run(["node","--check",p], capture_output=True, text=True)
assert r.returncode == 0, f"JS SYNTAX ERROR: {r.stderr}"
assert js.count("new Chart") == EXPECTED_CHARTS
assert sum(1 for l in js.split("\n") if l.strip()=="}") == 0, "stray brace!"
os.remove(p)
```
WHY: `node --check` is the ONLY reliable way to catch a broken `});`. A Python braces-count (`js.count("{")==js.count("}")`) PASSES even when there's an orphan `}` because it still balances. The orphan breaks `new Chart(...)` → browser silently renders nothing. Braces-count is NOT sufficient.

Test on a COPY first (never test against the production HTML you're about to ship):
```python
import shutil
shutil.copy(HTML, TMP); html = open(TMP).read(); new = rewrite_script(...); ...
```

## Hard Rules
- SSOT is source of truth. Dashboard is a VIEW — never hand-edit dashboard data, always regenerate from SSOT.
- Every generated HTML MUST pass `node --check` before commit / before telling Warren it's done.
- If `node` is absent → flag "JS syntax unchecked", do NOT claim green.
- Scope discipline: sync only the time-series charts you can derive from SSOT. Static snapshot charts (per-person earners, function breakdown) need deeper parsing — leave them or note the gap; don't fake them.

## Worked Example — Extra_Hours_Tracker.html (2026-07-11)
SSOT had June/May/April blocks. Dashboard `const months = ['May','Jun']` hardcoded → April missing. Built `sync_extra_hours_dashboard.py`:
- parse_blocks → 3 blocks (Jun,May,Apr)
- build_hours_trend → dual-axis OT/store + System Total WH
- build_ot_pay → OT cost ×50k fallback
- rewrite_script → updates `months` + 2 charts
- node --check gate → FIRST run FAILED (orphan `}` from `});`→`}` bug) → fixed script + manual orphan removal → re-check PASS, 7 charts, 0 stray braces.

Skill reference impl: `vault/scripts/sync_extra_hours_dashboard.py`.

## Pitfalls (from real failures)
- **Bold System row missed by regex** → block filtered, month vanishes from dashboard. Tolerate `**` on store name AND number cells.
- **Body ends with `}` not `});`** → broken `new Chart`, all subsequent charts blank. Always close the call.
- **Braces-count false-green** → balanced braces still allow orphan `}` elsewhere. Use `node --check`, not Python brace tally.
- **Orphan `}` persists across re-sync** → `re.sub count=1` leaves stray brace outside match. Assert zero stray braces post-rewrite.
- **Browser cache** → after fixing, Warren sees old broken chart. Tell him Ctrl+F5.
