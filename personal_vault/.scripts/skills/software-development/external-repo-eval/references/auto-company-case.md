# Case Study: Auto-Company → Hermes (2026-07-21)

> Runtime-locked repo (Claude Code). Decision: steal methodology, not code.

## Source
- **Repo:** MaxMiksa/Auto-Company (1.6k★, 502 commits)
- **What it does:** 14 AI agents (Bezos/Munger/DHH/...) run 24/7 autonomous company — ideate, build, deploy, market
- **Runtime:** Claude Code CLI + Codex CLI (heavily locked)
- **Platform:** macOS / Windows+WSL2

## B1 — Runtime-Lock Check
| Signal | Verdict |
|--------|---------|
| `.claude/agents/` (14 persona files) | 🔴 Claude-only |
| `.claude/skills/` (30+ skills) | 🔴 Claude format |
| `scripts/core/auto-loop.sh` calls `claude`/`codex` CLI | 🔴 Binary dep |
| `PROMPT.md` in Chinese, instructs Claude coordinator | 🔴 Agent-specific prompt |
| NOT an MCP server | ❌ No MCP path |

→ **"Install code" = ❌**. Khác runtime như app iPhone bỏ vô Android.

## B2 — What Was Worth Stealing

| Pattern | Hermes Equivalent | Decision |
|---------|------------------|----------|
| 14 expert personas | Already has stock-investment-committee (5), ops-mkt-manager-os (4-lens) | Skip — redundant |
| 24/7 loop + shared consensus.md | Already has cron + compress-memory + vault SSOT | Skip — Hermes better |
| Forced convergence (Cycle 1→2→3) | Missing → **STEAL** | Patch SOUL §5 + ops-case-lifecycle §5H |
| Explicit pre-mortem gate (Munger) | Missing → **STEAL** (Warren: "bố rất rất cần") | Patch safenet v1.1.0 |
| "Ship > Plan > Discuss" priority | Missing → **STEAL** | Patch SOUL §5 |

## B3 — Adapt for Free Model
- Auto-Company runs on Claude Sonnet/Opus (paid). Hermes = DeepSeek V4 Pro + OpenRouter free.
- 14 agents at once impossible → not ported (skip)
- 3 patterns stolen are methodology, not model-dependent — zero cost

## Deliverables
1. `safenet` v1.1.0 — Munger Pre-Mortem Gate (6 inversion questions + 6 mental models + kill criterion integration)
2. `SOUL.md` §5 — 2 new rows: "Ship > Verify > Simplify" + "Convergence Gate"
3. `ops-case-lifecycle` §5H — Stuck detection with 🔶 STUCK flag + 3 options (pivot/shrink/kill)

## Warren's Priority
"bố rất rất cần inversion thinking của Charlie Munger" — Pattern 2 was the #1 priority.

## Key Lesson
When evaluating external agent repos: the code is usually worthless (runtime-locked), but the methodology patterns are gold. Focus on: (1) what Hermes is MISSING (not what it already has), (2) what can be absorbed into EXISTING skills (not new builds), (3) what works on free models.
