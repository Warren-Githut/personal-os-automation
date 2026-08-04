# Warren Vault Knowledge
_Observed: 2026-06-12 | Path: vault/_

## Full Vault Structure
```
vault/
├── 00_CORE_LOGIC/          CONTEXT.md, DASHBOARD.md, SYSTEM_VIEW.md
├── 10_OPERATION_DATA/      12 rolling logs (01–12) + morning_briefs/ + synthesis
├── 30_KNOWLEDGE_BASE/
│   ├── wiki/               P&L_Budget/, menu_cogs/, labour_costs/, customer_experience/,
│   │                       lto_tracker/, lusine_operations/, marketing_growth/, SOP_POLICY_LUSINE/,
│   │                       warren_os/, + index files (WIKI_INDEX, WIKI_GRAPH, FRONTMATTER_CACHE)
│   └── raw/                READ-ONLY: raw dumps, CSVs, PDFs, recipes/
├── _cases/active/          20 case files
├── _cases/closed/          Archive
├── _inbox/                 tasks.md, CSVs, xlsx, ICS, photos
├── _journal/               2026-05.md, 2026-06.md
├── _growth/                Knowledge capture: atomic files + _INDEX.md
├── _ideas/                 Idea staging
├── _kilo/                  Kilo Code worktree config
└── _private/               Private notes
```

## Data Files (12 rolling logs)
01 Revenue, 02 HR, 03 COGS, 04 LTO, 05 Reviews, 06 GrabFood, 07 COL, 08 Incidents, 09 Hourly Cover, 10 Wastage, 11 Item Sales Star Horse, 12 Wage Structure.
Plus: morning_briefs_log.md, weekly_briefs_log.md, pulse_log.md, weekly_connections_log.md, weekly_ops_synthesis.md, OPERATION_INDEX.md.

## Active Cases (19 active: 10 HIGH, 9 MEDIUM)
HIGH: 2026-05_delivery-man-khanh-resign(LU3, 05/28 stale), 2026-05_pccc-lu3(LU3, stale), 2026-05_lu3-lu7-manpower-transition(06/08), 2026-05_lu5-manpower-van-khanh(07/20), 2026-05_lu5-relocation-crescent-mall(06/15), 2026-06_inventory-policy(06/09), 2026-06_lu3-revenue-recovery(06/14), 2026-06_relaunch-grabfood-ad(06/08 TODAY), 2026-06_takeaway-container-cost(06/14), 2026-06_lu5-food-lto.

## ORION Routine
- Mon 10am: morning brief → Slack DM + vault log
- Mon/Wed/Fri 10am: delta brief (COL, revenue, reviews, Kanban)
- Sun 8pm: vault lint
- Sun: weekly connections → weekly_connections_log.md
- Context update: đã merge vào `/ops-weekly-report` Phase 7 — chạy weekly report là đủ → CONTEXT.md §5
- Hermes training: ORION brief Step 9 checks hermes_training_log.md

## CONTEXT.md Section Map
- §1: Warren profile + non-IT rules (7) + Karpathy AI rules (4)
- §2: Store snapshot (dynamic; static specs in Lusine_Reference_Data)
- §4: Data cadence (13 inflows) + automations
- §5: "This Week" — up to 3 themes, Warren-confirmed
- §6: Thinking patterns — push-back guide for observer
- §6E: Constraints: moratorium on new specs, OIL liability 325M+, wiki Việtnamese policy (R4)

## Karpathy AI Rules
1. Think before you code — vague request = stop + state assumptions + options
2. Minimalism — minimum code, no overengineering
3. Edit like surgery — only touch lines that need changing
4. Execute by objective — vague → testable criteria

## 4 Ops Protocols (06/07)
1. Staff error → compensate customer, no blame culture
2. Guest flexibility → balance CX vs kitchen/bar control
3. Write-off bills → signature + photo + Warren heads-up
4. Ops reporting → brief Warren before BoD/other dept inquiries

## Key Staff Context
- Lộc (LU3 barista) exits 07/06 → Thảo starts 08/06 (training at LU7 with Jack)
- Jack (LU7→LU3): flagged for early exit during peak + walkout bill policy (team liable, Warren photo-approve)
- Định (LU7 bar sup): 21L condensed milk discrepancy → May service charge withheld
- Văn Khánh (LU5 Captain): stays until 30/06 → 2-3wk break → decision by 20/07

## COL Thresholds (from actual log — granular)
COL%: ✅ <15% | 🟡 15–20% | 🔴 >20%
SPLH: ✅ >350k | 🟡 250–350k | 🔴 <250k VND/hr