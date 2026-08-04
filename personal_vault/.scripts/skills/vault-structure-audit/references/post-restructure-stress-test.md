# Post-Restructure Stress Test

> **Use after:** any vault restructuring that renames folders, moves files, or changes INDEX structure.
> **Purpose:** Verify the new structure works end-to-end — not just that links aren't broken, but that the agent can navigate efficiently.

## Why a Stress Test?

A zero-broken-link report is necessary but not sufficient. The agent may:

- Still open extra files because the "Where To Go" map is ambiguous
- Find files slower because of missing INDEX onboarding
- Hit phantom files (INDEX entries that never existed)
- Encounter unremediated path references in frontmatter

The stress test catches these silently-broken cases.

## Methodology

### Step 1: Design 10+ Diverse Tasks

Pick tasks that cover:

| Category | Example | Why |
|----------|---------|-----|
| **Active wiki folder** | "Find LU3 P&L May" | Tests core domain→folder mapping |
| **Operations data log** | "COL this week" | Tests 10_OPERATION_DATA navigation |
| **Archived content** | "Old GrabFood report" | Tests archive navigation |
| **Root wiki file** | "Decision log about X" | Tests non-folder wiki files |
| **Cross-domain** | "Connections hub" | Tests 09_connections/ |
| **Edge case: empty file** | "Competitor intel" | Tests file existing but having 0 content |
| **Edge case: phantom file** | "Store roadmap" | Tests INDEX accuracy |
| **Deep nesting** | "Policy inside SOP folder" | Tests 3+ level navigation |
| **Frontmatter scope** | Check `scope:` fields in renamed folders | Tests metadata consistency |
| **Full-path wikilink** | Check `[[30_KNOWLEDGE_BASE/wiki/...]]` in POLICY files | Tests absolute paths |

### Step 2: Track Per-Task Metrics

| Metric | What to count |
|--------|--------------|
| **Files opened** | Every unique `read_file` call to find the answer |
| **Tool calls** | Every search/read/fetch needed |
| **Bugs found** | Record each: broken link, phantom file, stale path, wrong redirect |

### Step 3: Execute — One Task at a Time

For each task:
1. Use "Where To Go" or INDEX → navigate to the folder
2. Read the target file
3. Record: files opened, tool calls, any bug
4. Fix any bug immediately (patch → re-verify)

### Step 4: Analysis

| KPI | Target | Red Flag |
|-----|--------|----------|
| **Files per task** | ≤ 1.5 avg | > 2.0 means "Where To Go" is missing rows |
| **Calls per task** | ≤ 1.5 avg | > 2.0 means navigation is ambiguous |
| **Bugs found** | 0 pre-existing | Any → fix and re-add to test |
| **First-try accuracy** | 100% | Agent opens wrong folder → map needs refinement |

## Real-World Example

Warren's vault, 2026-07-01 (immediately after 10-folder numbering + Where To Go Phase 2):

| # | Task | Files | Calls | Bug Found |
|:-:|------|:----:|:-----:|:---------:|
| 1 | OIL liability tracking | 1 | 1 | — |
| 2 | Archived GrabFood Feb-Apr | 1 | 1 | `related: ["lusine_operations/"` (missing `06_`) |
| 3 | Store Ops Protocols v1 | 1 | 1 | — |
| 4 | Competitor intel | 1 | 1 | File empty (pre-existing data issue) |
| 5 | Cross-domain connections hub | 1 | 1 | — |
| 6 | Decision log (Store Ops) | 1 | 1 | `[[Policy/Store_Operations...]]` → wrong path |
| 7 | Recipe index reference | 1 | 1 | — |
| 8 | Store roadmap 2026-2027 | 1 | 1 | **PHANTOM FILE** — 36 broken wikilinks |
| 9 | LTO beverage summer | 1 | 1 | — |
| 10 | Staffing breakeven | 1 | 1 | `related: ["lusine_operations/"` (missing `06_`) |
| | **Avg** | **1.0** | **1.0** | **4 bugs (3 fixed, 1 flagged)** |

### Before → After Comparison

| Metric | Before (Phase 1 baseline) | After (stress test) | Change |
|--------|:-------------------------:|:--------------------:|:------:|
| Avg files per task | 1.6 | 1.0 | -38% ✅ |
| Avg calls per task | 1.6 | 1.0 | -38% ✅ |
| Pre-existing bugs | Unknown | 4 found | Detected |

## Stress Test as CI Gate

For any vault that is actively maintained and agent-navigated:

```
Before restructuring: measure baseline (5 tasks, track files+calls)
After restructuring: run full stress test (10+ tasks)
Gate: zero broken links, avg files ≤ 1.5
```

## Common Bug Patterns Found This Way

| Pattern | Detection Method | Fix |
|---------|-----------------|-----|
| **Phantom file** (INDEX entry, no file) | Read the referenced file → 404 | Remove from INDEX or create file |
| **Stale `related:` frontmatter** | Read FMF → compare path with folder name | `patch` path prefix |
| **Wrong wikilink path** (e.g., `[[Policy/...]]`) | Click link → 404 | Fix to full numbered path |
| **`scope:` out of sync** | Compare scope path with actual folder name | `patch` scope value |
| **Empty file** (INDEX references but 0 content) | File opening → no content | Add content or remove from INDEX |

## When to Run

- ✅ **After any folder rename** — immediately, before next commit
- ✅ **After adding "Where To Go" sections** — verify improvements
- ✅ **After moving files between folders** — verify wikilinks
- ✅ **Monthly deep audit** — as part of `/vault-structure-audit --execute`
- ❌ Not needed after single-file edits or content-only changes
