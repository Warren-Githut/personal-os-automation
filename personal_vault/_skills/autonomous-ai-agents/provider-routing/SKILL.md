---
name: provider-routing
description: Runtime model/provider routing based on task complexity. Auto-switches between cheap/fast and expensive/powerful models mid-session with cost quota, daily monitoring, and user override controls. Non-IT user optimized.
version: 1.0.0
author: Hermes (learned from Warren)
created: 2026-06-24
updated: 2026-06-24
tags: [hermes, provider, routing, cost-optimization, deepseek, non-it]
related_skills: [hermes-provider-setup, hermes-agent]
---

# Provider Routing

## Overview

When a Hermes profile has access to multiple models of different cost/quality tiers (e.g. DeepSeek V4 Flash vs V4 Pro), this skill defines the decision framework for **runtime routing**: when to use the cheap/fast model vs the expensive/powerful model within a single conversation.

This is NOT about static provider setup (API keys, proxy, config.yaml) — see `hermes-provider-setup` for that. This is about **at-runtime decisions** based on task complexity.

## When to Use This Skill

Apply when:
- Your profile has multiple models with a meaningful cost/performance spread (>=5x price difference)
- The user wants **cost-optimized defaults** with **automatic escalation** when the task requires it
- The user is non-technical and should never make model decisions manually
- You need guardrails (cost quota, override, visibility)

Do NOT use when:
- Only one model is available
- The user actively wants to choose models themselves per task
- The cost difference between models is negligible (<2x)

## Decision Framework

### Default: Use the cheap/fast model

All requests default to the cost-optimized model unless one or more trigger conditions are met.

### Trigger Conditions → Escalate to expensive/powerful model

| # | Condition | Rationale |
|---|-----------|-----------|
| 1 | **Multi-step tool chain (≥3 sequential calls)** | Complex reasoning benefits from stronger model |
| 2 | **Factual accuracy required** (vault queries, ops numbers, P&L analysis) | Cheap models hallucinate more on long-tail facts (up to 23-point gap on SimpleQA) |
| 3 | **Retry after failure** — cheap model returned error, wrong answer, or timeout | Fallback escalates, doesn't repeat the same failure |
| 4 | **User explicitly requests quality** ("verify this", "think carefully", "double-check") | User is paying attention — match their effort |
| 5 | **Long-horizon reasoning** (analysis across 50K+ context, multi-doc synthesis) | Stronger models maintain coherence better at depth |

### Flags that do NOT trigger escalation

- ❌ Simple Q&A ("what time is it?", "what's the weather")
- ❌ Bounded single-pass tasks (summarization, translation, classification)
- ❌ Routine chat turns, greetings, clarifications
- ❌ Speed-sensitive tasks (first-token latency matters more than quality)

### Think Mode Optimizer (cheap+thinking ≈ expensive)

When the cheap model supports a thinking/reasoning mode (e.g. DeepSeek V4 Flash Think Max):
- Route to **cheap + thinking** for moderate-complexity reasoning tasks
- Only route to **expensive** when cheap+thinking fails, or the task is genuinely multi-step agentic
- This captures most of the quality gap at a fraction of the cost

## Cost Quota Mechanism

### Core Parameters

| Parameter | Default | Notes |
|-----------|---------|-------|
| **Quota threshold** | 10% of total requests | Percentage of calls allowed on expensive model per window |
| **Window** | Monthly | Resets at calendar month boundary |
| **On hit** | Block further expensive calls + notify user immediately | User can override to unblock |
| **Override** | Chat command on/off toggle | User controls whether routing is active at all |

### Reporting Channels (configure per user)

| Channel | Frequency | Content |
|---------|-----------|---------|
| **Daily briefing** (morning brief) | Daily | One line: model usage % + call count |
| **Per-response tag** | Every response | e.g. `[⚡Flash]` or `[🧠Pro]` — position: end of response |
| **Threshold breach** | On hit | Alert + summary + override prompt |
| **Push notification** (Telegram etc.) | On threshold breach | Short alert with action |

### Counter Management

Maintain persistent counters:
- `total_calls` — all requests since window start
- `expensive_calls` — requests routed to expensive model
- `last_reset_date` — ISO date of last window reset

Reset triggers:
- Calendar month boundary passes → auto-reset
- User explicitly resets via `/routing reset`
- On/off toggle does NOT reset counters

## Implementation: Hermes CLI Sub-Session

When the decision framework says "route to expensive model" but Hermes is currently running on the cheap default model:

```
1. DETECT → task matches trigger condition(s)
2. SPAWN → hermes chat --model <expensive-model> --prompt "<task>" --no-stream --deliver local
3. COLLECT → read sub-session output from terminal stdout
4. PRESENT → wrap in current conversation with model tag [🧠Pro]
5. COUNT → increment expensive_calls counter
6. CHECK → if quota hit, block next escalation + notify
```

Benefits:
- ✅ Zero profile switching (no logout/login)
- ✅ Zero config changes
- ✅ Non-disruptive — user sees only the response + model tag
- ✅ Sub-session runs headless, invisible to user

### Pitfalls

- **Hermes CLI may not be in PATH** — use absolute path or `npx hermes` depending on setup
- **Sub-session latency** — spawning a new session costs ~2-5s overhead, don't use for trivial escalations
- **Sub-session model mismatch** — verify `--model` flag is supported by the running Hermes version
- **Counter persistence** — in-memory counters die with session restart; use a lightweight JSON file for durability
- **Race condition** — if multiple tasks escalate simultaneously (batch tool calls), ensure only one sub-session spawns per task

## User Controls (Non-IT Command Pattern)

| Command | Effect |
|---------|--------|
| `/routing on` | Enable automatic routing (default) |
| `/routing off` | Disable routing, all requests use default model |
| `/routing override` | Allow expensive model despite quota hit |
| `/routing status` | Show current usage stats (X% expensive, Y/Z calls) |
| `/routing reset` | Reset counters (start new window) |

## UX Contract (Non-IT Design Principles)

1. **Zero friction** — user never makes model decisions. Routing is automatic.
2. **Transparent** — model tag on every response so user can audit decisions.
3. **Accountable** — daily report so user knows what's happening.
4. **Controllable** — on/off + override. User always has final say.
5. **Forward-compatible** — cost/quality benchmarks change. Document the *decision shape* (task complexity triggers), not hardcoded model names. Update references/ when providers release new models.

## Verification

After implementing routing:

- [ ] Default request uses Flash → confirm via model tag
- [ ] Request matching trigger condition uses Pro → confirm via model tag
- [ ] Quota at 9.9% → next escalation allowed
- [ ] Quota at 10% → next escalation blocked + notification sent
- [ ] `/routing override` → escalates despite quota hit
- [ ] `/routing off` → all requests use default model
- [ ] Daily report shows accurate usage stats
- [ ] Counter survives Hermes restart (persistent JSON)
