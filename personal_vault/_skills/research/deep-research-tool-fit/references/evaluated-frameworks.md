---
name: evaluated-frameworks
description: Condensed knowledge bank of external frameworks/repos evaluated for Warren's stack — verdict + borrowed concepts. Add one entry per deep-research pass.
type: references
---

# Evaluated Frameworks (condensed)

## Loopy (Forward-Future/loopy) — 2026-07-19
- **What:** Agent skill (installs into Codex/Cursor/Claude Code via `npx skills add`) + public "Loop Library" catalog of repeatable AI-agent workflows (feedback loops with verify + stop condition). 2.8k⭐, MIT.
- **Verdict:** ❌ DON'T INSTALL. Wrong runtime (no `--agent hermes`), wrong domain (catalog = software-eng loops: "Overnight Docs Sweep", "improve test reliability"). Warren already has bounded-feedback workflows via skills + cron + verify-parser-output gate.
- **Borrowed concepts (applied):**
  1. **Run Receipt** → `vault/10_OPERATION_DATA/cron_receipts/` folder + README format `Action | Evidence | Outcome | Stop`. Every cron writes one after running.
  2. **Loop Doctor** → `/audit-automation` monthly cadence (FLAG ONLY, zone 🟡) + Google Calendar "Monthly Loop Doctor" (day-1 15:00, OAuth user-visible RRULE — NOT service account, SA events invisible to Warren).
- **Source:** github.com/Forward-Future/loopy — README.md + skills/loopy/SKILL.md + AGENTS.md.
- **Lesson:** Reject ≠ stop. Extract 2–3 transferable concepts, propose as vault/skill improvements.
