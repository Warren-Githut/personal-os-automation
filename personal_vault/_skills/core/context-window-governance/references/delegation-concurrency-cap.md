# Delegation Concurrency Cap (warren-profile) — 2026-07-25

`delegate_task` batch mode rejects > `max_concurrent_children` tasks. **This profile caps at 3.**

Symptom when exceeded:
```
Too many tasks: 5 provided, but max_concurrent_children is 3.
Either reduce the task count, split into multiple delegate_task calls,
or increase delegation.max_concurrent_children in config.yaml.
```

## Correct split for simplify-code (4 reviewers) + code-review-and-quality (1)

`/simplify-code` says "fan out 4 reviewers in one batch" — that alone is fine (4 > 3? NO, 4 > 3 → also rejected).
So even the 4-reviewers-alone batch is REJECTED at cap=3.

**Working pattern:**
- Batch 1: `delegate_task(tasks=[Reuse, Quality, Efficiency])` → exactly 3, accepted.
- Batch 2: `delegate_task(goal=Altitude)` → 1 accepted.
- Batch 3: `delegate_task(goal=Multi-axis review)` → 1 accepted.

Subagents run in ISOLATED contexts and wait on each other; consolidated result
re-enters chat. Parent context does NOT balloon — so running heavy review near
the 150K "dumb zone" is SAFE (Bố approved override 2026-07-25).

## Why this matters
Bố's "trên 150k dumb zone → slice + handoff" rule is OVERRIDDEN for heavy *review*
of finished code precisely because subagent context is offloaded. Inline heavy
review would break the rule; delegated review does not.
