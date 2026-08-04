---
name: auto-reviewer
description: "Post-output independent review gate for personal-profile — automatically spawns a SEPARATE Reviewer Node via delegate_task (inherits the chat's free model, NOT hardcoded) after Hermes finishes any major artifact, so a fresh-context agent checks it before Warren reads. Thin router over reviewer-node; adds the explicit 'done' trigger + mandatory deliver token."
version: 1.0.0
author: Hermes
trigger: "auto — after any artifact meeting the 'done' definition (see When-to-call)"
category: core
related_skills: [reviewer-node, safenet, verify-parser-output]
---

# auto-reviewer — Post-Output Independent Review Node

> Thin router over `reviewer-node`. Adds: (1) the explicit "done" trigger so Hermes self-delegates, (2) the mandatory deliver token. The reviewer is a SEPARATE node — spawned via `delegate_task` with CLEAN context (no Hermes raw data/transcript), and it inherits the SAME free model as the chat (NO hardcoded model — Warren directive 2026-07-22).

## When to call (the "DONE" definition — Hermes self-delegates)
Call auto-reviewer IMMEDIATELY when ALL hold:
- **(A)** Hermes just produced a deliverable artifact for Warren or the vault:
  - Report (health summary / finance review / legal timeline / weekly personal digest)
  - Dashboard / parser output
  - New or edited `.md` in `personal_vault/` `_cases/` `_inbox/` `wiki/`
- **(B)** Artifact contains ≥1 of: a number (sleep hours / weight / money / %), OR a strategic conclusion / action recommendation (health plan, finance decision)
- **(C)** The task used ≥3 tool calls

Do NOT call for: clarify questions to Warren, lookups ≤2 calls, session-start bootstrap.

**Hard discipline:** BEFORE delivering the artifact to Warren, Hermes MUST hold a reviewer verdict. No verdict = not done, do NOT deliver.

## How to call (delegate_task — separate node)

**Bước chuẩn bị (BẮT BUỘC — tránh placeholder rỗng):**
1. `read_file` `C:/Users/khoans/Documents/Personal_OS/personal_vault/00_CORE_LOGIC/ANCHORS.md` → gán `anchors_summary` = nội dung file thật (để reviewer check A1 source / A2 no-diagnosis / A4 finance / A7 segregation...).
2. `skill_view(name="reviewer-node")` → gán `checklist` = bảng 5 trục (KHÔNG tự viết lại).
3. `artifact` = output Hermes vừa làm.

```python
delegate_task(
    goal="Review the output below. Return PASS or FAIL + a specific list of errors.",
    context=f"""### OUTPUT TO REVIEW:
{artifact}

### CHECKLIST (5 axes — loaded from reviewer-node, do NOT duplicate):
{checklist}

### ANCHORS (frozen — read carefully, full content below):
{anchors_summary}

### RETURN FORMAT (reviewer subagent ONLY returns review text — do NOT print any 🔍 token):
PASS or FAIL
If FAIL → list each: [TYPE] description + specific location
If PASS → "PASS — [short reason]"
""",
    # model / provider OMITTED → inherits the chat's free model (e.g. hy3:free).
    # Do NOT hardcode a model (Warren directive 2026-07-22).
    # CONTEXT MUST contain ONLY {artifact}+{checklist}+{anchors_summary}.
    # Never inject Hermes transcript / tool results (clean-context rule).
)
```

## Reviewer rules (from reviewer-node)
1. **Clean context:** reviewer sees ONLY output + checklist + anchors. NOT Hermes raw data/transcript.
2. **No edits:** reviewer only flags; Hermes (orchestrator) fixes.
3. **Max 2 rounds:** FAIL → Hermes fixes → re-review. FAIL 2nd time → escalate to Warren with both reviews.
4. **PASS ≠ perfect:** PASS = no checklist errors; improvements noted separately.
5. **Model:** inherits chat free model. If quality poor → report to Warren, do NOT hardcode a model.

## Mandatory deliver token
After review, **ONLY Hermes (orchestrator) prints** this token on the delivery — the reviewer subagent must NOT (C1 fix). Token format is exact; safenet checks substring `🔍 REVIEWER:`:

```
🔍 REVIEWER: ✅ PASS (model=<inherited free model, e.g. hy3:free>) — [short reason]
```
or, after FAIL #2 (HARD BLOCK — artifact NOT delivered, M3 fix):
```
🔍 REVIEWER: 🔴 FAIL [2] (model=<...>) — escalated, BLOCKED pending Bố
```
Missing token on a major delivery = violation (same class as missing boot / safenet token).

## Integration
- `safenet` routes "major output to Warren" → this skill (mandatory before deliver).
- If the artifact is numeric → run `verify-parser-output` FIRST (numbers fact-checked), THEN this node checks the whole (logic / consistency / format / completeness).
- Pair with `reviewer-node` (loads the 5-axis checklist + ANCHORS summary from there — do NOT duplicate).

## Pitfalls
- **Hardcoding model** — violates Warren 2026-07-22 directive: use the same free model as the chat, do NOT pin.
- **Self-review theater** — Hermes must NOT review its own output and call it PASS; always spawn the separate node.
- **Context leak** — never pass Hermes's raw data/transcript to the reviewer; that turns it into a rubber-stamp.
- **Empty anchors_summary** — MUST load `C:/Users/khoans/Documents/Personal_OS/personal_vault/00_CORE_LOGIC/ANCHORS.md` into the variable; never leave the placeholder (reviewer can't check A1-A9 without it).
