# "Where To Go" — Agent Navigation Map for INDEX Files

## What

A **domain→folder mapping table** appended to the end of vault INDEX files. Tells the agent (Hermes, Claude Code, any LLM) exactly which folder/file to open for each domain topic, eliminating guesswork and extra file reads.

## Why

Without a "Where To Go" section, an agent reading `00_WIKI_INDEX.md` sees a catalog of files but doesn't know WHICH ONE to open for a given question. It must infer the mapping from file names and descriptions — often incorrectly, wasting tool calls.

With "Where To Go", the agent can route in zero additional reads:

```
WHERE TO GO — Wiki
  P&L, budget         → 01_P&L_Budget/
  Customer experience  → 03_customer_experience/
  Labour cost, COL     → 04_labour_costs/
```

## Measurement: Before → After

Real baseline from Warren's vault (2026-07-01):

| Task | Before (no map) | After (with map) | Improvement |
|------|:---------------:|:----------------:|:-----------:|
| Find LU3 P&L | 3 files / 3 calls | **1 file / 1 call** | -67% |
| Find Google Review W26 | 2 files / 2 calls | **1 file / 1 call** | -50% |

The map saves 1-2 file reads per ambiguous query. Over a 100-query week, that's ~150 fewer tool calls.

## Format

Use a Markdown table at the END of the INDEX file (after the file catalog, before any Update Protocol section):

```markdown
## Where To Go — Wiki

| Nếu Warren hỏi về... | Hermes mở file này |
|----------------------|--------------------|
| **P&L, budget, variance, breakeven** | `01_P&L_Budget/` |
| **SOP, policies, procedures** | `02_SOP_POLICY_LUSINE/` |
| **Customer experience, Google Reviews, CX metrics** | `03_customer_experience/` |
| **...** | `...` |
```

Table headers in Vietnamese (for Warren's vault), values are folder paths in backticks.

## Which INDEX files to add to

| File | Scope | Example row |
|------|-------|-------------|
| `00_WIKI_INDEX.md` | Wiki domains (P&L, CX, Marketing, etc.) | `P&L, budget → 01_P&L_Budget/` |
| `OPERATION_INDEX.md` | Weekly operational logs (Revenue, COL, GrabFood, etc.) | `Google Reviews this week → 05_Google_Review_Weekly_Log.md` |
| `CASES_INDEX.md` | Case directories (active, closed, projects) | `Active cases → _cases/active/` |

## Maintenance

- **When adding a new folder:** Add a row to "Where To Go" in the relevant INDEX file.
- **When renaming a folder:** Update the row's path value.
- **The agent auto-reads this section at session start** (after reading SOUL.md and CONTEXT.md).

## Relationship to INDEX structure

```
00_WIKI_INDEX.md:
  01. P&L_Budget          ← file catalog (for human browsing)
  │  file | period | type | key_insights
  │  ...
  02. SOP_POLICY_LUSINE   ← file catalog
  │  ...
  ...
  Where To Go ← agent routing table (for AI navigation)
  Update Protocol
```

The catalog (per-section file tables) and the map (Where To Go) serve different purposes:
- **Catalog:** Lists everything in a domain. Good for browsing and exact file lookup.
- **Map:** Maps questions to folders. Good for the agent's first routing decision.

Both are needed. Never replace one with the other.
