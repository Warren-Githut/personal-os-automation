---
name: debug-hygiene
description: "Debug hygiene: verify before claiming; no real writes."
version: 1
author: hermes
license: mit
metadata:
  hermes:
    tags: [debugging, verification, warren-preference, side-effects, capture-sleep]
    related_skills: [debugging-and-error-recovery, verify-parser-output, telegram-capture-gate]
---

# Debug Hygiene (Warren-specific)

## When to Use
Load when debugging any system with real side effects: vault writes, GSheet sync,
Telegram send, git push, external API calls. Especially capture-sleep / Telegram
bot / GSheet sync work. Also load after Warren says "you lied / fabricated / xạo"
or "đừng vòng vo" — those signal the hygiene rules below were violated.

Concrete Telegram poller recipe in `references/telegram-bot-debugging.md`.

## Core rules (HARD — earned in 2026-08 capture-sleep debugging)

### 1. Never call real write functions during debugging
Do NOT invoke these FOR REAL while investigating:
`write_vault()`, `sync_and_commit()`, `send_msg()`, `git commit/push`,
`gsheet.append()/update()`, or any external send.

Why it bites:
- Dirties production state (vault / GSheet / Telegram).
- **Breaks `is_duplicate`**: a fake entry you wrote makes the REAL message look
  like a duplicate → real message gets silently dropped (this happened: a test
  `write_vault` created a fake 2026-08-03 entry, so Bố's real 7h40 message was
  flagged duplicate and dropped).
- Masks the real bug — you think "it worked" but it was your test write.

Instead:
- Use a temp file copy (`Path(src).copy(temp)`), or
- Mock the side-effecting fn and capture call args with `io.StringIO` / `unittest.mock`, or
- After ANY manual real write during a test, `git checkout -- <file>` to restore clean state.

### 2. Verify before claiming success
Never report "synced / written / pushed / sent" without RUNNING it + READING BACK:
- GSheet: after sync, read back the sheet, confirm the row/date exists.
- Vault: after write, grep the file for the entry (`### DATE`).
- Telegram: after `send_msg`, confirm returned `message_id` is an int > 0 (or read back).
- If you only *think* it worked → say "I haven't verified" — do NOT claim.

**Existence claims run BOTH directions, and a script's own "✅" is never the evidence.**
- Confirm PRESENT: read the artifact back off disk, cross-assert TỪNG field against the
  input the user gave (render `field | source | written | match?`). A one-row parse is
  not exempt — `99/62` written as `96/62` looks exactly as confident as a wrong sum.
- Confirm ABSENT before claiming anything is missing: the file is written by several
  actors (cron poller, chat paste, manual edit, other sessions), so a date missing from
  *your view* usually means captured elsewhere. Grep the whole range first. A false
  "gap" sends the user to re-supply data they already gave. Absence of evidence in one
  window is not evidence of absence in the file.
- A parser printing "✅ synced / +1 row" is a CLAIM, not proof. Re-read the target.

### 3. Be straight when wrong
If Warren says "you lied / fabricated / why didn't you answer" → own it immediately.
Show actual state. Do not rationalize or blame the tool. Admit the gap, then fix with evidence.

### 4. Verify the verifier's own API before trusting it
Read-back helpers live in the same codebase under test, so a stale name or wrong
signature in a skill/instruction file fails the gate before it can verify anything.
Before calling a documented helper (sheet reader, DB client, read-back fn):
- `grep -n "def " <module>.py` to confirm it exists AND its exact arity.
- Call it with the real signature — do not pass a path/key arg "because the doc said
  so" when the definition takes none.
- If the documented helper does not exist, the INSTRUCTION is wrong: fix the source
  of truth. Do not keep retrying variants of the name from memory.

### 5. Scoped commit, then verify the remote moved
After a real run: `git status --short` first (know the tree was clean, don't ship
another session's work), `git add` ONLY the file this run changed, commit, push, then
`git log --oneline -1` + `git status -sb` to confirm the remote actually advanced.
A successful `git push` line in the transcript is the claim, not the proof.

### 6. Verify deletions thoroughly (cleanup/retirement tasks)
When retiring folders, skills, or data stores (e.g., `_journal/`, `_inbox/`, `_personal_memory_raw.md`):

- Confirm actual deletion with `ls` or `find` — don't trust the `rm -rf` exit code alone.
- Sweep ALL references: production files (vault, skills, scripts, commands, templates) AND .scripts/ SSOT copies.
- Check both `personal_profile` AND `warren-profile` (shared skills via symlink).
- Update ontology, memory loop references, and SOUL.md consistently.
- Historical records (source citations like `Source: _inbox/01_unprocessed/...`) are OK to leave — they're past-tense, not active pointers.

### 7. Memory loop abolition = update ALL layers
See `references/verify-evidence-retention.md` for what evidence to keep when retiring a store.
When abolishing a raw log or intermediate store:
- SOUL.md vault structure table
- SOUL.md memory loop section
- PERSONAL_MEMORY.md (or WARREN_MEMORY.md) references
- PERONTOLOGY.md type table
- compress-memory skill
- hermes-profile-memory-architecture skill
- All template/references that mention the old path

## When Warren pushes back on a factual claim
If he corrects a fact you asserted ("the other days I already logged in another chat"),
he is right and the claim is a bug, not a style nit. Own it in ONE line, correct the
record, and do NOT re-verify, re-explain, or re-narrate the run — a short factual
acknowledgement plus the corrected state is the whole response. Long defensive
explanation after a correction reads as arguing with the user.

## Verification discipline
Prefer ad-hoc verify scripts (tempfile, prefix `hermes-verify-`) that mock side effects
and assert on captured call args — NOT suite-green claims. Clean up the temp script after.

See `references/telegram-bot-debugging.md` for the concrete Telegram poller recipe
(offset reset, getUpdates queue check, draft-as-standalone vs reply_to).

### 8. A failing test is not evidence the CODE is wrong
Triage the test before the source. Most failures in this codebase's shape are the
test's fault, and "fixing" correct code to satisfy them is how a behavior-preserving
task turns into a silent regression.

- **The case may never reach the branch it names.** A fixture can trip an earlier
  guard and fall into a different branch, so the assertion fails for a reason
  unrelated to the change. Re-derive ALL the guard conditions the case must
  satisfy simultaneously, then check the fixture against every one.
- **The expectation may encode behavior the code never had.** Before treating an
  assertion as the spec, run that same case against the COMMITTED baseline
  (`git stash` your edit, run, `git stash pop`). Identical behavior ⇒ the code is
  correct and the test is wrong. They differ ⇒ a real regression. This settles it
  in one run; reasoning about intent does not.
- **Baseline references drift.** An assertion that greps `git show HEAD:file`
  starts failing the moment you commit the fix, because HEAD is now the fixed
  version. Pin such checks to the explicit commit that still contains the bug.
- **"This looks redundant" is a hypothesis, not a finding.** Sort/filter/guard
  lines that appear dead are often load-bearing on a specific input shape. Delete
  in a scratch run and diff the result; if the selected row changes, it stays.

When a verify script and the implementation disagree, say which one you believe and
why BEFORE editing either. Naming the wrong culprit costs a wasted edit cycle and
erodes trust in the next run.

### 9. Behavior-preserving refactor: prove it with a golden-output diff
"It imports", `py_compile` OK, and "the existing tests pass" all pass on a change
that silently alters output. Proof is a diff, not a green light.

1. Build a fixed case matrix over the BRANCH BOUNDARIES, not a happy path: each
   threshold ±1, empty/missing inputs, decimal and single-item values, long
   histories, reversed ordering, plus a read-only probe against the real
   production file.
2. Run the matrix → `golden-before.txt`. Apply ONE change at a time.
3. Run again → `golden-after.txt`. `diff before after` must be empty.
4. Every non-empty diff line is either an unintended change or a deliberate one.
   Deliberate output changes ship as a SEPARATE bug-fix commit, never folded into
   a refactor commit, so the diff stays reviewable.
5. Re-run the pre-existing suites too — the matrix is additive, not a replacement.

Exercise all call paths, not just the obvious one. A helper gaining a parameter
must be threaded through EVERY caller; grep the symbol to prove the list is
complete, and where a batch can contain several entries, verify intra-batch
ordering by checking that a second entry in the same run sees the first.
When a batch's items are not yet on disk, the shared state must be threaded in
memory — refreshing from disk mid-loop silently misses the siblings.

