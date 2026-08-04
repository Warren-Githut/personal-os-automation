---
name: session-start
description: "Session bootstrap — canonical load order every session. Reads SOUL§6 → vault MEMORY → USER → vault CONTEXT → index scan → git → highlight. Profile-agnostic: paths defined in each profile's SOUL.md §Quick Reference."
version: 2.0.0
author: Hermes
trigger: "/session-start (auto-run at session begin)"
category: core
tags: ['bootstrap', 'session', 'startup', 'core']
related_skills: ['compress-memory']
---

# /session-start — Profile-Agnostic Session Bootstrap

> **Purpose:** Deterministic load order so GG starts every session in the same known state. Profile-agnostic — each profile's SOUL.md defines its specific vault paths.
>
> **Paths SSOT:** This skill references SOUL.md §Quick Reference for all vault file paths. Every profile MUST maintain a `## Quick Reference` section in its SOUL.md with paths for MEMORY.md, ANCHORS.md, CONTEXT.md, and parser_script_checklist.md.

---

## 🚨 HARD GATE — unconditional first action (STRUCTURAL, non-discretionary)

> **Root-cause lesson (2026-07-18):** Enforcing bootstrap on the agent's *discretion* fails — when a session opens with a low-stakes greeting ("hi"), the agent skipped the reads and answered directly. The fix is **structure, not willpower**: SOUL §6 HARD GATE forces this skill to load every session, and the consolidated GATE TOKEN line makes the failure *observable* so Warren catches it instantly.
>
> **Rule (mandatory, NO exception):** Run steps 1–4 (SOUL §6 → vault MEMORY → USER → vault CONTEXT) **BEFORE any response** — including "hi"/"hello"/greetings. There is NO "low-stakes" exception. Steps 5–7 follow before substantive work.
>
> **This is structural enforcement:** the skill loads via SOUL §6 every session; the token is the proof-of-work. Discretion-based compliance is explicitly rejected.

### GATE TOKEN → consolidated `✅ GATES:` line at END (mandatory on every first-turn response)

> **Token gate:** consolidated into ONE line at the END of the response (not scattered at top).

The first response of every session MUST contain the gate line (end of response). Format:
```
✅ GATES: boot✓ freeze✓ safenet✓ archive✓
```
or, if bootstrap not done:
```
✅ GATES: boot🔴 CHƯA bootstrap — [reason]
```

The specific gate tokens per profile are defined in each SOUL.md §GATE TOKEN.

**Quick-Q skip:** If Bố prefixes `quick:` → response ends with `⚡ no-gate (quick-Q)` (skip freeze/safenet token, answer directly, still verify silently). See SOUL.md §GATE TOKEN.

---

## Override rule

`vault MEMORY.md` **overrides** built-in memory on conflict. If a fact in MEMORY.md contradicts something GG "remembers" natively → MEMORY.md wins.

---

## STEP0 — VERIFY ACTUAL READ (anti-fake-token)

> The `✅ GATES: boot✓` line is only honest if steps 1–4 were *actually read this turn* via a tool call, not "remembered from system prompt". Enforce:
> - Steps 1–4 MUST each be a real `read_file` (or `search_files`/`session_search`) call this session — not a claim.
> - Before printing `✅`, GG must have tool output for all: SOUL §6 (system prompt is NOT enough → confirm via read_file or skill_view), vault MEMORY.md, USER.md, vault CONTEXT.md.
> - If ANY of 1–4 not actually read this turn → token MUST be `boot🔴 CHƯA bootstrap — [which file missing]`.
> - Never print `✅` from memory alone. A false `✅` = trust breach.

### 📋 What GG read this session (print in body, first-turn only)

Print a short checklist in the response body so the user can verify at a glance (gate line goes at END via `✅ GATES:`):

```markdown
Read at session start:
  [1] SOUL.md §6        — identity/core rules (system prompt + confirmed)
  [2] <PROFILE>_MEMORY.md — preferences/corrections (read_file ✓)
  [3] ANCHORS.md         — frozen rules (read_file ✓)
  [3b] VAULT_MAP.md      — vault schema/folder governance (read_file ✓)
  [4] USER.md            — user profile (read_file ✓)
  [5] CONTEXT.md         — live state (read_file ✓)
  [6] CONSISTENCY_LOG.md — open entries check (read_file ✓ or 'none')
```
(Replace ✓ with ✗ + reason for any not actually read. PROFILE = profile name from SOUL.md identity.)

---

## 9-step load order (run in this exact sequence — ALL mandatory, non-discretionary)

Paths reference `SOUL.md §Quick Reference` — each profile defines its own vault paths there.

1. **SOUL.md §6** — identity, philosophy, core rules (profile root — auto-loaded by Hermes; confirm with skill_view or read_file).
2. **Vault MEMORY.md** — apply Preferences / Corrections / Patterns / Lessons Learned. Path from SOUL.md §Quick Reference (`MEMORY_PATH`).
3. **ANCHORS.md** — frozen rules GG may NEVER change unilaterally. Path from SOUL.md §Quick Reference (`ANCHORS_PATH`).
   **3.5. Parser/script/skill checklist** — hard gate before creating/editing parsers. Path from SOUL.md §Quick Reference (`CHECKLIST_PATH`).
   **⚠️ DOTFOLDER NOTE:** Real scripts live in vault `.scripts/` (DOTFOLDER, hidden) — NOT `vault/scripts/`. `search_files` is blind to dotfolders → always use `terminal ls` or `find`. Agent `delegate_task` also blind → pass absolute path.
   **3.6. VAULT_MAP.md** — vault schema/ontology + folder governance. Path from SOUL.md §Quick Reference (`VAULT_MAP_PATH`).
4. **USER.md** — user profile (role, style, preferences). Auto-loaded from profile's `memories/USER.md`.
5. **CONTEXT.md** — live state + this week priorities. Path from SOUL.md §Quick Reference (`CONTEXT_PATH`).
6. **Index scan** — read index files of relevant areas (paths from SOUL.md §Quick Reference).
7. **`git log --oneline -5`** — recent commits in vault root. Path from SOUL.md §Quick Reference (`VAULT_ROOT`).
8. **MEMORY.md highlight** — show top 3–5 relevant items → ask "Bố cần gì?" (end of boot).
9. **CONSISTENCY_LOG check** — if vault CONSISTENCY_LOG.md exists and contains any entry with `status: open` (unresolved), emit ONE line after boot checklist. Path from SOUL.md §Quick Reference (`CONSISTENCY_LOG_PATH`).

**10. Router auto-load** — load skill `using-agent-skills` (router + 12 Matt Pocock techniques).
**11. Skill SSOT sync reminder** — any skill change this session MUST follow the Post-Skill Output Template (SSOT → archive → runtime → diff-verify).

---

## Notes

- Steps 1–4 are file reads; do them before answering anything.
- Steps 5–7 are pre-work before substantive tasks; no token gate on these, but they must run before acting on real data.

---

## Pitfalls

- **Skipping bootstrap on a greeting (2026-07-18).** Opening with "hi" is NOT a reason to skip steps 1–4. Always emit the `✅ GATES: boot✓` line at END of response.
- **Discretion-based enforcement decays.** Pair instructions with an observable artifact (the gate line) or it will silently fail again.
- **Don't claim a read you didn't do.** Token MUST say `boot🔴` with reason — never fake `✅`.
- **Trust disk, not memory, for file paths.** On Windows MSYS, `search_files` returns empty / IO error even when the file EXISTS. Use `terminal ls`/`find` to verify paths at session start.
- **MEMORY.md is REFERENCE, NOT sacrosanct — verify claims on disk.** Before using a specific claim from MEMORY.md as a PREMISE for analysis (especially system/tech setup), MANDATORY verify on disk.
- **External-framework evaluation also must verify claims on disk.** Don't claim existing equivalents from memory — check reality.
