---

description: "Musk Algorithm applied to any target — file, SOP, wiki page, idea, process. 5-step ruthless deletion lens."
updated: 2026-06-02
---

# /ruthless — Musk Algorithm Deletion Lens
# v1.0 | 2026-05-31
# PURPOSE: Apply Elon Musk's 5-step algorithm (Question · Delete · Simplify · Accelerate · Automate-last) to any target in Warren's world — files, SOPs, wiki pages, ideas, processes.
# POSITION IN WORKFLOW: Any artifact ? /ruthless ? RD verdict ? action (edit / delete / archive / restructure)
# NOT FOR: Plans that need >file review ? use /review-plan. Already-coded features ? use /review-audit.

---

## Usage

```
/ruthless [file name, path, or paste text]
```

**Auto-detect modes:**
- File matched in vault (by name or path) ? read file ? ruthless
- Match >1 file ? list for Warren to choose (show path + excerpt first 3 lines)
- Match 1 file ? show path, ask confirm before running
- No file match ? treat input as raw text ? ruthless directly (no confirm)

---

## Protocol — 5-Step Musk Algorithm (mandatory, no skipping, no reordering)

### STEP 1 — Question requirements

Read target. Answer:
- What problem is this target solving?
- Is the problem real, or is it a symptom?
- If this target is deleted, what is the actual consequence? (specific, not vague)
- Who/what is affected?

### STEP 2 — Try to delete

Identify parts of the target that can be completely deleted.
- List each component/section/step of the target
- Give KEEP/DELETE verdict for each
- Minimum 1 DELETE — otherwise ? INVALID, redo
- After 2 retries still can't find DELETE ? output "? RD UNABLE TO FIND DELETIONS — target is minimal or analysis exhausted. Keep as-is recommended unless new context emerges."

### STEP 3 — Simplify (after deletion)

For the remaining parts:
- Can it be simpler? (prose ? bullet? 5 steps ? 3 steps?)
- Do NOT simplify what should have been deleted in Step 2

### STEP 4 — Accelerate cycle time

- From start to result, how long does it take?
- Can any intermediate steps be cut?
- How long is the feedback loop to know right/wrong?

### STEP 5 — Automate (last, with warning)

- Are you automating a process not yet verified manually?
- If YES ? flag CRITICAL: "Run manual N times first, then automate."
- If NO ? proceed

---

## Output Format

```
??????????????????????????????????????
RUTHLESS VERDICT — [target summary 1 sentence]
??????????????????????????????????????

TARGET: [file name / path / raw text summary]
SIZE: [n lines or n characters]

[RD] STEP 1 — QUESTION: [2-3 line answer — root problem]

[RD] STEP 2 — DELETE:
  - [component 1]: KEEP / DELETE — [reason]
  - [component 2]: KEEP / DELETE — [reason]
  - ...

[RD] STEP 3 — SIMPLIFY: [only remaining parts after Step 2]
  - [suggestion 1]
  - [suggestion 2]

[RD] STEP 4 — CYCLE TIME: [estimate] — cut: [suggestion]

[RD] STEP 5 — AUTOMATION CHECK: [SAFE / RISK — broken process?]

??????????????????????????????????????
RECOMMENDED ACTION:
  ??? DELETE / ?? CUT [n] components / ?? RESTRUCTURE / ? KEEP AS-IS

REASON: [1-2 sentences — based on Step 2 analysis]
??????????????????????????????????????
```

### Map to actionable outcome

| Verdict | Action |
|---|---|
| ??? DELETE | Warren deletes file / deletes content portion |
| ?? CUT components | Warren edits file, deletes components marked DELETE |
| ?? RESTRUCTURE | Create plan for restructure (/generate-plan ? /review-plan) |
| ? KEEP AS-IS | Do nothing — target is already optimal |

---

## Rules

- Steps 1-5 mandatory, no skipping, no reordering. Automate is last step = mandatory condition.
- Step 2 must have minimum 1 DELETE — otherwise, redo. After 2 retries ? escalate message.
- Don't suggest automation before verifying manual workflow.
- Don't modify files directly — only recommend action. Warren decides to edit.

---

## Anti-patterns

- ? Automate Steps 2-3 when Step 1 is not yet complete — must follow correct order
- ? Skip Step 2 (delete) to go straight to Simplify — wrong Musk Algorithm
- ? Skip Step 4 (cycle time) because "not relevant to content files" — cycle time applies to processes, not just file content
- ? Modify files directly — /ruthless is diagnostic, not a surgical tool
- ? Use when target has already been /review-plan reviewed — RD persona is already in review plan

---

## Integration

/ruthless is the **standalone version** of the RUTHLESS DELETER persona in /review-plan.
- In /review-plan: RD only evaluates deletion of 1 plan (already has structure + components)
- /ruthless: RD evaluates anything (file, SOP, wiki page, idea text) — more flexible, pre-filter

**Flow suggestion:** /ruthless ? RD recommends restructure ? /generate-plan ? /review-plan ? code

---

**v1.0 | 2026-05-31 | Created per Warren's request: standalone Musk Algorithm command for arbitrary targets.**
