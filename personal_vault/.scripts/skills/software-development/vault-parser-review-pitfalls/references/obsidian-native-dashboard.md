# Obsidian-Native Dashboard (no plugin) — Mermaid pattern

Warren wanted Item Sales dashboard visible inside Obsidian. The HTML (`item_sales_trend.html`)
has data but Obsidian preview **blocks `<script>`** → charts never render. Fix: emit a
**Mermaid** note — Mermaid is BUILT-IN to Obsidian (no community plugin needed).

## Why Mermaid, not Dataview/Chart plugin
- Obsidian core ships Mermaid renderer. `dataview` / `obsidian-charts` require enabling
  community plugins (Bố must tick in UI). Mermaid = zero-setup, opens instantly.
- HTML `<script>` + Chart.js: works in browser, dead in Obsidian preview.

## Generator shape (`emit_item_sales_mermaid.py`, in `10_OPERATION_DATA/.parsers/`)
1. Parse the tracker markdown: `## 2026-Wxx | date` headers + `### Store Summary` table.
2. Regex gotchas (real, cost ~6 failed runs):
   - Header sep row is `|------|----:|-------:|----:` → separator regex must be `\|[-: |]+\|`
     (NOT `\|[-| ]+\|` — the `:` breaks the latter).
   - Cell values like `242.5M` → strip `M`/`*`/`,`/`₫` THEN `float() * 1_000_000`
     (NOT `/1e6` — `242.5`/1e6 = 0.0002 → rounds to 0.0).
   - Skip rows where store name lowercased ∈ {`store`,`system`,``}.
3. Build `xychart-beta` blocks:
   ```mermaid
   xychart-beta
       title "System Net Rev (M) & Items"
       x-axis [W18, W19, ... W29]
       y-axis "Net Rev (M)"
       bar [678.4, ...]
       line [5309, ...]
   ```
4. Write `Item_Sales_Dashboard.md` (frontmatter + mermaid + a plain markdown summary table).
5. Bố opens the note in Obsidian → charts render live from the tracker.

## Re-run cadence
Tracker updates weekly (parser `--live`). Re-run `emit_item_sales_mermaid.py` after each
parser run to refresh the dashboard note. Wire as a post-step in the parser, or a cron.

## Full browser link (for the HTML version, has data)
file:///C:/Users/khoans/Documents/Warren_OS_Local/vault/30_KNOWLEDGE_BASE/wiki/dashboards/item_sales_trend.html

## Obsidian-native link
file:///C:/Users/khoans/Documents/Warren_OS_Local/vault/30_KNOWLEDGE_BASE/wiki/dashboards/Item_Sales_Dashboard.md

## Extra gotchas (2026-07-27 session)
- **Sort-order print bug:** `sorted(weeks, key=lambda x: x[0])` → W18..W29 (string compare
  correct: `2026-W18` < `2026-W29`). `latest = sorted[-1]` = W29. Do NOT print `weeks[-1]`
  (that is the RAW order = W29 first → mislabels "latest 2026-W18"). Print the sorted tail.
- **HTML "trắng" root cause (confirmed):** `item_sales_trend.html` has VALID data
  (`PAYLOADS` JSON parses, 12 weeks, all fields present). Chart.js is embedded inline.
  If Bố reports blank, it is the OPEN SURFACE: Obsidian preview blocks `<script>` → blank;
  a real browser (Chrome/Edge, `file:///`) shows charts. Don't chase a "data bug" in a valid
  HTML — the data is fine, Obsidian strips JS. Browser tool also BLOCKS `file://` as private,
  so headless-render diagnosis is impossible; rely on `json.loads(PAYLOADS)` validity + Bố's
  confirm of open surface. Mermaid note is the Obsidian-safe alternative.
