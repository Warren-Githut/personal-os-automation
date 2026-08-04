# Post-Run Critique Pattern (AUTOMATION_HEALTH.md)

**Origins:** Loop Engineering (cobusgreyling/loop-engineering) — post-run critique as continuous improvement mechanism for autonomous loops.

**File:** `vault/00_CORE_LOGIC/AUTOMATION_HEALTH.md`

## Purpose

Every LLM-driven cron job records a self-critique after each run. Warren reads the file weekly to detect:
- Noise patterns (false alarms the cron keeps flagging)
- False positives (wrong decisions made by the LLM)
- Recurring adjustments (one change per run to improve quality over time)

## Pattern

After finishing its main task, every LLM-driven cron job MUST:

1. Assess what happened during the run
2. Prepend an entry to `AUTOMATION_HEALTH.md` in this EXACT format:

```markdown
## [cron-name] @ HH:MM DD/MM
- Noise: <items flagged but not actionable>
- FP: <false positives if any>
- Adjust: <1 change for next run>
```

3. If cron found nothing to process or ran cleanly: record `none` for all fields

## Cron Job Prompt Integration

Add this as the FINAL step in every LLM-driven cron prompt:

```
### Step N: Post-Run Critique (ALWAYS — even if no work done)
Prepend a critique entry to vault/00_CORE_LOGIC/AUTOMATION_HEALTH.md:
## [cron-name] @ HH:MM DD/MM
- Noise: <items flagged but not actionable>
- FP: <false positives if any>
- Adjust: <1 change for next run>

If nothing processed: write Noise=none / FP=none / Adjust=none.
```

**Critical:** The `ALWAYS` keyword is mandatory — without it, the LLM may skip writing when there's nothing to report, which defeats the purpose of trend tracking.

## Current Jobs Using This Pattern (warren-profile)

| Cron | Step added | 
|------|-----------|
| col-queue-watcher (2m) | Step 6 |
| review-queue-watcher (1m) | Step 8 |
| daily-ops-brief (09:30) | Step 7 |
| stock-broker-fetch (09:00) | Last step |
| stock-route-pending (09:15) | Last step |
| mem0-cleanup (CN 09:00) | Last step |
| audit-automation-weekly (CN 19h) | Last step |

## Why This Works

- **Tiny overhead per run** (3 lines, ~50 tokens)
- **Compounds over time** — after 30 runs, you can see which cron jobs are noisy and which adjustments actually stuck
- **Actionable** — each `Adjust:` entry is one concrete change to try next time
- **No extra monitoring** — Warren reads one file, not many

## Pitfalls

- **LLM skips critique on empty runs** — fix by adding `(ALWAYS — even if no work done)` to the step heading
- **Entries prepend before main heading** — template comment block in AUTOMATION_HEALTH.md helps LLM understand correct placement (after frontmatter + template, before entries)
- **Only for LLM-driven crons** — deterministic `no_agent` scripts don't need critique (no reasoning to audit)
