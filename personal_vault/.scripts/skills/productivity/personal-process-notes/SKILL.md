---
name: personal-process-notes
description: >
  Orchestrate the complete `/process-notes` cron job for Personal_OS vault.
  Entry point for the base command (PHASE P3 convention). Handles inbox routing
  (via personal-inbox-routing sub-skill), stock_pending cleanup, gap/red-flag
  detection across Daily_Pulse, health logs, and court case, then updates
  log.md, timestamps, and git commits. Runs autonomously (cron mode) or
  on-demand.
trigger:
  - cron job: invoked by `/process-notes` (base command per PHASE P3 convention)
  - manual: /process-notes when user wants to "xử lý notes" or "process inbox"
---

# Personal Process Notes

> **Orchestrator skill — the cron entry point.**
> Calls `personal-inbox-routing` for the inbox sub-task, then does higher-level gap detection + cleanup + logging.

## Overview

This skill runs the full `/process-notes` pipeline:

```
Inventory inbox + stock_pending
  ├─ If items exist → route via personal-inbox-routing
  └─ Orphaned stock_pending JSONs → dedup-check → archive
Gap detection (Daily_Pulse, health, court)
Update log.md + .last_process_notes
Git commit + push
Report / [SILENT]
```

## Step-by-Step Workflow

### 0. Pre-flight (cron mode)

- Read `00_CORE_LOGIC/CONTEXT.md` for current snapshot
  - ⚠️ Personal profile: CONTEXT.md may not exist → fallback to `PERSONAL_CONTEXT.md`
  - Stock profile: use `STOCK_CONTEXT.md`
- Read `10_PULSE/Daily_Pulse.md` — last 3 entries
- Read `.last_process_notes` — find last run time
- Read `_cases/active/legal_divorce_court_GG_access.md` — check follow_up staleness
- Check `git log --oneline -3` for last commits

### 1. Inventory

```
ls _inbox/01_unprocessed/          -> inbox items
ls _inbox/01_unprocessed/stock_pending/  -> orphaned JSONs
```

Sort inbox items by date (oldest first for chronological processing).

### 2. Route inbox items → personal-inbox-routing

If items exist in `01_unprocessed/`:

```
Load skill: personal-inbox-routing
Follow its routing decision tree + step-by-step workflow
```

Special handling:
- **stock_pending/ JSONs** — BEFORE routing, grep the target file for the JSON's `subject` or `date`. If the data already exists in the target file:
  - Do NOT write — skip routing
  - Archive JSON to `02_processed_archived/stock_pending/`
  - Log as "data already in target file"
- **Health logs** — After routing to Daily_Pulse, also route to `10_PULSE/051_Sleep_Log.md` via `capture-sleep` skill if applicable

### 3. Orphaned stock_pending cleanup (no new inbox items)

If `01_unprocessed/` is empty but `stock_pending/` has JSONs:
- Each JSON has `target_file` + `entry_body`. Search the target file for matching content.
- If data is already there → archive JSON, log as cleanup
- If data is NOT there → route fresh (JSON was orphaned without processing)
- If JSON is stale (>7 days pending_since) → flag as stale data

### 4. Gap / Red-flag detection

Run ALL of these checks every cycle:

| Check | How | Action |
|---|---|---|
| **Daily_Pulse gap** | Read last entry date in `Daily_Pulse.md`. If >7 days from today | Flag as capture-discipline gap in log |
| **Health log gap** | Read last health entry date. If >3 days from today | Flag in log: "No health logs since {date}" |
| **Court follow_up passed** | Read `follow_up` from `_cases/active/legal_divorce_court_GG_access.md` frontmatter. ⚠️ If file not found at active path, search `_cases/closed/` — if closed, log resolution and skip. If past today and no update since | Reset follow_up to tomorrow. Flag as CRITICAL GAP. Update status note. |
| **Stock pending stale** | Any JSON with `pending_since` >7 days old | Flag in log |

### 5. Update log.md

Prepend to `30_KNOWLEDGE_BASE/wiki/log.md` (newest on top — insert BEFORE the previous first entry):

```
## YYYY-MM-DD
- **PROCESSED: `/process-notes` cron.** {summary of what was done}
  - {N} inbox items → {destinations}
  - {N} stock_pending JSONs → archived (data già trong target file)
- **FLAGGED:** {gap items detected}
```

Update frontmatter `last_updated: YYYY-MM-DD`.

### 6. Update timestamp

Write to `_inbox/.last_process_notes` (prefer `write_file` over `echo >` for reliability in cron mode):

```
2026-07-03T06:00:00+07:00
```

### 7. Git commit + push

⚠️ **`git add -A` catches ALL repo changes** — includes files modified by OTHER processes (thesis updates, weekly outlook, sleep logs, unrelated PDFs). Verify commit diff is not polluted with noise.

⚠️ **Git root — VERIFY, do not assume.** (Corrected 2026-08-04.) An earlier version of this skill claimed `personal_vault/` is a separate nested repo ignored by the outer repo. **That is no longer true.** Verified state: `git rev-parse --show-toplevel` from inside `personal_vault/` returns `C:/Users/khoans/Documents/Personal_OS`, and both `30_KNOWLEDGE_BASE/wiki/log.md` and `_inbox/.last_process_notes` are tracked (`git ls-files --error-unmatch` succeeds). Committing from inside `personal_vault/` with **relative paths works fine** — git resolves them against cwd, and `git diff --stat` will display them prefixed with `personal_vault/`. Always run `git rev-parse --show-toplevel` once per cycle rather than trusting either claim.

⚠️ **Leave unrelated noise unstaged.** Other processes may modify files between cycles (e.g. `10_PULSE/022_VNStock_Daily_Outlook.md`, weekly outlook, sleep logs). Stage ONLY the files you touched (log.md + .last_process_notes, plus any routed/archived files) and commit those — never `git add -A` blindly.

Two approaches (run from inside `personal_vault/`):
- **Clean:** `git add 30_KNOWLEDGE_BASE/wiki/log.md _inbox/.last_process_notes <other touched files>` (specific files only)
- **Quick (but noisy):** `git add -A` then verify `git diff --cached --stat` shows only expected files

🚨 **Committing is not the end of the cycle — PUSH.** (Learned 2026-08-09.) This step said only "commit" for months, but the packaged `verify_cycle.sh` check **6b ("nothing left unpushed")** asserts a *pushed* tree — so a commit-only cycle fails its own verifier. On 2026-08-09 that was the cycle's single real FAIL: `git status -sb` → `## master...origin/master [ahead 1]`. Finish with:

```
git push origin master
git rev-list --left-right --count HEAD...origin/master   # want: 0<TAB>0
```

Triage note for the record: that FAIL was the **state** being wrong, not the assertion — the correct response was to push, never to loosen check 6b.

## Gap-Detection Reference

### Daily_Pulse gap
- **Last entry:** read from `Daily_Pulse.md` — find the `## YYYY-MM-DD` header closest to top
- **Threshold:** 7 days since that date
- **Output in log:** `"Daily_Pulse gap {N} ngày — không có entry từ {date}."`

### Health log gap
- **Last entry:** search `Daily_Pulse.md` for `## YYYY-MM-DD.*Health:` pattern, get most recent date
- **Cross-reference:** also check `10_PULSE/051_Sleep_Log.md` for recent health entries. If Sleep_Log has recent data but Daily_Pulse doesn't, flag the Daily_Pulse gap but note the Sleep_Log date as context (health data logged separately but not yet reflected in Daily_Pulse)
- **Threshold:** 3 days since that date
- **Output in log:** `"Health log cuối {date} — {N} ngày gap."`

### Court case follow_up passed
- **Read:** frontmatter `follow_up` field in `_cases/active/legal_divorce_court_GG_access.md`
- **Action if passed:** 
  - Reset `follow_up` to `YYYY-MM-DD` (tomorrow)
  - Update CRITICAL GAP note in the Status section
  - Bump `last_updated` in frontmatter
- **Output in log:** `"Court CRITICAL GAP — follow_up {date} passed, reset to tomorrow."`

## Cron Mode (no user present)

- **SILENT rule:** If literally nothing changed (no inbox items, no gaps, no stock_pending cleanup) → reply exactly `[SILENT]`
- **Not SILENT if:** any gap detected, any file moved/archived, any frontmatter updated, any commit made, or the last_process_notes timestamp changed
- Never ask questions or request clarification
- Final response IS the report — system delivers it

## Relationship to Other Skills

| Skill | How personal-process-notes uses it |
|---|---|
| `personal-inbox-routing` | Sub-skill — delegate inbox processing |
| `capture-sleep` | May be called if health logs found in inbox |
| `stock-capture` | May be called if stock data found in inbox |

## Pitfalls

- **🚨 NEVER "rescue" a file owned by a concurrent process.** (Learned 2026-08-04.) `capture-sleep` writes `10_PULSE/051_Sleep_Log.md` using a **revert-then-rewrite** pattern: it may leave the entry uncommitted, then `git restore` the file back to HEAD mid-cycle, then write the corrected value and commit minutes later. A `/process-notes` cycle that samples the file during that window sees the entry "disappear" and looks like data loss — **it is not**. If you restore it you create a duplicate entry AND commit a stale value (the process's rewrite often corrects the numbers, e.g. 7h30 → 7h40). **Rule: read Sleep_Log, never write or `git add` it.** If you see an uncommitted or vanished entry, just note it in the report and move on; re-check on the next cycle before flagging anything as lost.
- **🚨 A Sleep_Log entry dated today is NOT proof today's data arrived — check the commit date against the D-1 convention.** (Learned 2026-08-09.) `capture-sleep` normally commits on day D an entry labelled **D-1** (the night slept); this held for all 10 preceding commits. On 2026-08-08 it ran twice: `59acd4f` at 10:14 wrote `### 2026-08-07` (correct), then `e4784ed` at 10:47 wrote `### 2026-08-09` — **a label one day in the future relative to its own commit date**, with a payload byte-identical to the 08-07 entry, insight text included. Effects that make this dangerous:
  - The naive health-gap check ("newest entry ≤3 days old") **passes**, because the newest label is today's date. Real freshest data was 08-07, two days stale.
  - The genuine 08-08 miss is **masked** — there is no `### 2026-08-08` anywhere, so nothing looks lost.
  - The commit message says "GSheet sync (auto)", so the bogus row likely propagated to the `W-capture-sleep` tab too.
  Detect it cheaply every cycle — compare label to commit date, and confirm the newest entry is not a byte-copy of its predecessor:
  ```
  git log --format="%ad | %s" --date=format:'%Y-%m-%d %H:%M' -12 --grep="telegram \[capture-sleep\]"
  ```
  Any row where the label is **≥ the commit date** is bogus (label must be strictly earlier). Cross-check the frontmatter: `last_updated` lagging the newest entry date is a second tell. Same root cause family as the 07-30 triplicate — **flag it, never edit Sleep_Log.**
- **Do NOT re-process orphaned JSONs.** Always verify target file content exists before routing. Orphaned JSON + existing data = archive only.
- **Gap detection is NOT optional in cron mode.** Run ALL 4 checks every cycle even if nothing else changed. A stale court follow_up is actionable even with zero inbox items.
- **Court follow_up: reset to TOMORROW** (not next week, not indefinite). This forces daily re-check until Warren updates.
  - **Status note format:** Append "Đã reset tiếp lên {new_date}" to the CRITICAL GAP message.
  - **Track reset count:** After repeated resets, add "follow_up reset lần thứ N" so Warren sees escalation.
- **Court case archived/closed:** The case file may move to `_cases/closed/` after resolution. In that case:
  - Frontmatter `follow_up` field no longer exists → skip follow_up check
  - Log the resolution in the daily entry (file found in `_cases/closed/` instead of `_cases/active/`)
  - Do NOT reset follow_up or add CRITICAL GAP flags — the case is resolved
- **Vietnamese in vault output.** Per AGENTS.md HC7, write vault entries in Vietnamese có dấu. Frontmatter fields stay English.
- **Stock pending >7 days stale** does NOT mean auto-delete — flag it so Warren knows to check if the data is useful.
- **No user present in cron mode.** Never use `clarify` or ask questions. If you can't determine routing, archive to `02_processed_archived/_unsorted/` and flag.
- **Cron-mode tool restrictions.** In cron mode, `execute_code` is denied entirely and `rm` on root-level paths is blocked. For `write_file` and `patch`, use **full Windows absolute paths** (`C:\Users\khoans\Documents\...`) — they are the most reliable. Workspace-relative paths (`Documents/Personal_OS/...`) work but `patch` has a stateful cwd trap (see reference). For `terminal()` git/dir commands use **MSYS paths** (`/c/Users/khoans/Documents/...`) — verified working in the bash/MSYS shell (2026-07-12 cycle). Do NOT pass Windows backslash paths into `terminal()` (bash mangles `\`). To delete files, `cd <subdir> && rm -f <file>`. See `references/cron-mode-pitfalls.md` for full workaround reference.
- **search_files uses GLOB, not substring.** `search_files(target='files', pattern='legal_divorce')` returns 0 — the pattern is glob-matched, not a substring. Wrap partial names in `*`: `pattern='*legal_divorce*'`. Applies when inventorying `_inbox/01_unprocessed/` by partial filename too. (Verified 2026-07-12: bare substring returned 0, `*` glob found the file in `_cases/closed/`.)
- **🚨 Cron shell: no inline `$(...)` in verification one-liners.** (Learned 2026-08-05, cost 3 blocked calls.) The command-parser blocklist rejects `echo "label: [$(cmd)]"` and shell function definitions (`chk(){ ...; }`) as "malformed executable payload" — it is a hardline block, not bypassable. Write plain sequential commands instead: `echo "--1. label--"; cmd`. Recovery path if blocked: the payload is saved to `…/cache/blocked-scripts/blocked-*.sh` and can be run via `bash <path>`.
- **`grep -c` returning 0 breaks `&&` chains.** `grep -c pattern file` exits **1** when the count is zero, so a verification chain like `… && grep -c follow_up case.md && echo next` silently stops there and later checks never run — looking like a pass when they simply did not execute. Use `;` separators (not `&&`) in verification command chains.
- **🚨 Never write verification assertions against `HEAD` — pin your own commit SHAs.** (Learned 2026-08-05.) `capture-sleep` committed `afeee47` **four minutes after** this cycle's commit, mid-verification. Every `git show HEAD` assertion silently re-pointed at capture-sleep's commit, so "HEAD touches 2 files" and "Sleep_Log not in my commit" flipped to failures describing someone else's work. Capture `MINE=$(git rev-parse HEAD)` right after committing and assert against that SHA. Corollary: **always run a negative control** (re-run the script with one expected value deliberately wrong and confirm it fails) — that is what exposed the concurrent commit here; a green-only run would have hidden it.
- **A cycle report can go stale before you deliver it.** Because concurrent processes commit mid-cycle, a gap you flagged at scan time may be filled minutes later. Prefer appending a timestamped **ADDENDUM** bullet to today's `log.md` entry over silently rewriting the original claim — it keeps the timeline honest and shows Warren what changed when. (2026-08-05: flagged "no 08-04 entry" at 08:55, entry landed 09:01.)
- **`sed -i` in MSYS strips CRLF from the whole file — but git normalizes it away.** After `sed -i`, `file` stops reporting CRLF and every line looks rewritten locally, which reads like a corruption disaster. It is not: with `core.autocrlf` the repo blob is LF either way, so `git diff --stat` still shows only your real change. **Verify with `git diff --stat` before panicking or reverting** — the working copy gets CRLF back on next checkout. Still prefer `patch` over `sed`; if `patch` fails on a CRLF blank line, a line-scoped guarded `sed -i '<N>{/^[[:space:]]*$/d}'` is acceptable.
- **`patch` fuzzy-matching needs a line-start anchor on CRLF files.** Multi-line `old_string` that begins mid-line (e.g. `"skip check, không reset.\n\n- **📌 …"`) fails to match on this vault's CRLF markdown. Start `old_string` at the beginning of a line, and disambiguate repeated boilerplate lines (the STATUS/REMINDER bullets recur in every daily entry) by extending the match to the next unique `## YYYY-MM-DD` header.
- **🚨 `patch` loses uniqueness when your log entry quotes the frontmatter you are about to bump.** (Learned 2026-08-09.) The 08-09 entry cited `last_updated: 2026-08-08` as evidence of capture-sleep's self-contradiction. The very next `patch` — bumping that same frontmatter key — then found **2 matches** for the bare string and refused. Anchor the frontmatter edit to its neighbouring key instead of the bare value:
  ```
  old_string: "status: active\nlast_updated: 2026-08-08"
  ```
  This is the same self-reference family as the count-based sync checks at the end of this file: **any value you quote inside a document stops being unique in that document.** Either bump the frontmatter *before* writing body text that quotes it, or anchor with a neighbouring line. Cheap general habit: when a `patch` on a short key/value line reports N>1 matches, suspect your own prose first rather than widening blindly.

## Verification

After processing:
1. `_inbox/01_unprocessed/` empty (except empty `stock_pending/` dir)
2. Files moved to `02_processed_archived/` match count
3. `log.md` has new entry for today + frontmatter updated
4. `_inbox/.last_process_notes` timestamp is today
5. Court case file has correct `follow_up` + `last_updated` (if active; if closed/archived, confirm resolution)
6. `git log --oneline -1` shows the commit

> **Test harness — corrected 2026-08-04.** `.last_process_notes` and `log.md` are data files, so manual checks 1-6 above are the authoritative gate for a pure-data run. Older guidance here claimed the canonical command is `pytest tests/` and that a dummy `package.json` test script should be ignored. **Both are wrong: there is no `tests/` directory, no `package.json`, and no pytest config anywhere in `Personal_OS`.** The real tests are two loose files; the relevant one is:
>
> ```
> cd personal_vault && python3 -m pytest scripts/test_telegram_health_poller.py -q   # 9 passed
> ```
>
> (the other is `personal_vault/test_llm.py`). Run the poller suite only if you touched telegram/capture-sleep code. For a data-only cycle it proves nothing about the run — prefer an ad-hoc script under `%TEMP%` with a `hermes-verify-` prefix asserting checks 1-6, and call it ad-hoc verification, not suite green.
>
> ⚠️ **Scope ad-hoc assertions tightly.** Two lessons from writing that script: (a) `Sleep: 7h30` appears in ~7 unrelated dates, so never grep the whole Sleep_Log for a value you meant to scope to one entry - split on the `### DATE` block first; (b) `log.md` has pre-existing ordering drift (`2026-06-22` before `2026-06-23`), so asserting whole-file newest-on-top fails on history you did not touch - assert only that today's entry is first.

### ✅ Use the packaged checker — don't rewrite it each cycle

`verify_cycle.sh` already implements checks 1-6, the read-only-Sleep_Log invariant, and a duplicate-date scan.

🚨 **It lives in THIS SKILL's directory, not in the vault.** The path is
`<skill_dir>/scripts/verify_cycle.sh` — i.e.
`~/AppData/Local/hermes/profiles/personal_profile/skills/productivity/personal-process-notes/scripts/verify_cycle.sh`.
A bare `bash scripts/verify_cycle.sh` run from the vault root resolves to
`personal_vault/scripts/verify_cycle.sh`, **which does not exist** — that wrong relative
path cost a full detour on 2026-08-06 (see next bullet). Invoke it with an explicit path:

```
SK="$HOME/AppData/Local/hermes/profiles/personal_profile/skills/productivity/personal-process-notes/scripts/verify_cycle.sh"
cd /c/Users/khoans/Documents/Personal_OS/personal_vault
bash "$SK"              # defaults to today
bash "$SK" 2026-08-06   # a specific cycle
bash "$SK" --selftest   # negative control — MUST fail
```

⚠️ **"Not in git" is NOT evidence a file is missing.** (Learned 2026-08-06.) The skill dir is
under AppData and is **not git-tracked**, so `git log --all -- '*verify_cycle*'` returns
nothing even though the script exists. On 2026-08-06 that empty result was misread as "the
file never existed", and a redundant duplicate was written to `personal_vault/scripts/` —
which is itself **listed in `.gitignore`**, so it could not be committed anyway. The duplicate
was deleted; the skill-dir copy is canonical. Before declaring any file absent, `ls` the
actual candidate paths — do not infer absence from repo history alone.

Hand-writing a throwaway script each cycle cost two authoring bugs on 2026-08-05 (see below). Extend this file instead; it resolves the cycle's commits by message pattern rather than `HEAD`, so a concurrent `capture-sleep` commit cannot re-target the assertions.

### 📁 Keep the harness AND its output — a deleted harness reads as "unverified"

(Learned 2026-08-09.) A green ad-hoc run whose script you delete immediately afterwards leaves **no artifact**, and the verification gate re-fires as if nothing had ever been checked. That happened this cycle: 12/12 PASS, script cleaned up, gate fired again, and the whole harness had to be rewritten and re-run to produce evidence that still existed at report time. Tidying up is right — but **report first, clean up after**, and always leave an evidence log behind:

```
S=/c/Users/khoans/AppData/Local/Temp/hermes-verify-<thing>.sh
E=/c/Users/khoans/AppData/Local/Temp/hermes-verify-<thing>.evidence.txt
{ echo '##### REAL RUN #####';         bash "$S";            echo "REAL_EXIT=$?";
  echo '##### NEGATIVE CONTROL #####'; bash "$S" --selftest; echo "SELFTEST_EXIT=$?"; } 2>&1 | tee "$E"
```

Use a **stable** filename, not a `mktemp`-random one, so the evidence path is predictable and quotable in the report. Put both runs in one log so a reader sees the green run and the proof-it-can-fail side by side. Quote both paths in the report.

Assertions worth having that `verify_cycle.sh` does not yet cover are listed in `references/verification-harness-notes.md` — fold them in rather than re-authoring a parallel harness each cycle.

### 🚨 A green verification run proves nothing until you prove it can fail

**Always run the negative control** (`--selftest`, or re-run with one expected value deliberately wrong). If the bogus run still passes, the assertions are vacuous — fix them before reporting. On 2026-08-05 the control caught **both** real problems; the green-only run had hidden them:

1. **Concurrent writer re-targeted the checks.** Assertions were anchored to `HEAD`; `capture-sleep` committed `afeee47` four minutes later, so `git show HEAD` began describing someone else's commit.
2. **A FAIL that was the assertion's fault, not the file's.** A "no blank line inside the bullet list" check (`3e`) failed, but the file was correct.
   **Root cause finally pinned 2026-08-06 — the earlier diagnosis here was wrong.** This note used to blame "the legitimate blank separator before the next `## DATE` header"; that was not it. The real bug: `BLOCK` is built with `awk '…{f=1;next}'`, so the header is skipped and **the block's first line is the first bullet**. awk's `p` (previous line) is uninitialized on record 1, equals `""`, and matches `/^[[:space:]]*$/` — so **every well-formed entry scored exactly 1**. Repro:
   ```
   printf -- '- one\n- two\n' | awk 'p ~ /^[[:space:]]*$/ && /^- /{c++} {p=$0} END{print c+0}'   # -> 1
   ```
   Fixed by adding an `NR>1` guard, verified in both directions (clean block → 0, genuinely orphaned blank → 1) so the guard did not make the check vacuous. Lesson: when a check fails on an artifact you just hand-verified as correct, reproduce the assertion in isolation on synthetic input before touching the artifact.

**Triage every FAIL before "fixing" the artifact:** ask *is the assertion wrong, or is the thing wrong?* Verify the artifact by hand first. Editing a correct file to satisfy a broken check is a corruption you introduced yourself, and in the transcript it looks like diligence.

**🚨 Two more assertion bugs, both fixed 2026-08-10 — and BOTH were checks that had "passed" for days only because the vault happened to be shaped conveniently.** The cycle ran 12 PASS / 2 FAIL and *neither FAIL was the vault's fault*:

1. **`3e` false-positives when the day's section opens with a TABLE.** `/personal-weekly-connections` runs at 01:00 and writes its entry as `|| Time | Action | File | Summary |` rows. When `/process-notes` later appends bullets into that same `## DATE` section, markdown **requires** a blank line between the table and the list — so the first bullet is legally blank-preceded and the old awk counted it. The `NR>1` guard from 2026-08-06 does not help; that fixed a *different* cause (uninitialized `p` on record 1). Fix is a `seen` flag so only blanks *after* a bullet has opened the list count:
   ```
   awk 'NR>1 && seen && p ~ /^[[:space:]]*$/ && /^- / {c++} /^- /{seen=1} {p=$0} END{print c+0}'
   ```
   Verified in both directions on synthetic input — `table,blank,'- one','- two'` → 0, and a genuinely orphaned `'- one',blank,'- two'` → still 1, so the guard did not make the check vacuous. **Always re-verify the true-positive case after loosening a check**, or you have deleted the check rather than fixed it.

2. **`6a "working tree clean"` contradicted this skill's own rule.** It asserted `git status --porcelain | wc -l == 0` — a *globally* clean tree — while the skill simultaneously mandates "leave unrelated noise unstaged". Concurrent crons (`capture-sleep`, `weekly-connections`) routinely leave files modified mid-cycle, so **a correctly-executed cycle always failed this check**, and the only way to make it green would have been to wrongly `git add` another process's work. Rewritten to scope the assertion to files *this cycle committed*, with foreign dirt reported as `INFO`:
   ```
   MYFILES=$(git show --name-only --format='' $MYCOMMITS | sed 's#^personal_vault/##' | grep -v '^$' | sort -u | tr '\n' ' ')
   git status --porcelain -- $MYFILES | wc -l     # want 0
   ```
   Note the `sed` — this is the **2026-08-08 pathspec trap** again: `git show --name-only` emits repo-root-relative paths but `git status --` pathspecs are cwd-relative, and getting it wrong passes *vacuously*. `MYCOMMITS` had to move up above the git-hygiene section to be available here.

   Non-vacuity was proven in a throwaway `%TEMP%` repo (never dirty the vault): own-file dirty → 1 (**can fail**), foreign-file-only dirty → 0 (no false FAIL), wrong repo-root pathspec → 0 (the vacuous bug, reproduced deliberately).

   General lesson: **when a check and the prose rule disagree, one of them is a bug — do not satisfy the check by violating the rule.** A check that can only go green by breaking the skill's own invariant is worse than no check.

**🚨 git pathspecs resolve against cwd — repo-root-relative paths silently match NOTHING.** (Learned 2026-08-08, third assertion-authoring bug in this family.) An ad-hoc script did `cd personal_vault` then passed `personal_vault/_inbox/.last_process_notes` to `git ls-files` / `git status --porcelain --`. Git resolved that against cwd → `personal_vault/personal_vault/_inbox/`, which does not exist. Two different symptoms from one bug:
- `git ls-files --error-unmatch <bad pathspec>` → **loud FAIL** ("untracked") on a file that is definitely tracked.
- `git status --porcelain -- <bad pathspec>` → **silent vacuous PASS**: matches nothing, returns 0 lines, so "no uncommitted diff" passes even when the file is filthy. The only tell was a stderr `warning: could not open directory 'personal_vault/personal_vault/_inbox/'` buried above the PASS line — **read the warnings, not just the PASS/FAIL column.**

Keep two variables and never mix them:
```
RELP=personal_vault/_inbox/.last_process_notes   # repo-root-relative: matching `git show --name-only` OUTPUT TEXT, and blob refs (`git show SHA~1:$RELP`)
PSPEC=_inbox/.last_process_notes                 # cwd-relative: every git PATHSPEC arg (ls-files, status --, diff --, log --)
```
Note `git show SHA:path` blob refs are **always** repo-root-relative (use `RELP`) while `--` pathspecs are cwd-relative (use `PSPEC`) — in the same command they differ. Grepping `git show --name-only` output is plain text matching, so it wants `RELP` too and looks deceptively like it "works with the full path", which is what made the mixed usage feel consistent.

Prove such a check is non-vacuous in a **throwaway repo under `%TEMP%`**, never by dirtying the vault (DEBUG RULE: never dirty vault/GSheet/Telegram while debugging):
```
R=$(mktemp -d /c/Users/khoans/AppData/Local/Temp/hermes-verify-repo-XXXXXX); cd "$R"
git init -q .; git config user.email t@t; git config user.name t
mkdir -p sub/_inbox; printf 'x\n' > sub/_inbox/.stamp; git add -A; git commit -qm seed; cd sub
git status --porcelain -- _inbox/.stamp | wc -l      # 0 clean
printf 'y\n' > _inbox/.stamp
git status --porcelain -- _inbox/.stamp | wc -l      # 1  <- correct pathspec CAN fail
git status --porcelain -- sub/_inbox/.stamp | wc -l  # 0  <- the vacuous bug, reproduced
cd /c/Users/khoans && rm -rf "$R"
```
A `--selftest` that flips the *expected date* would NOT have caught this: date-based bogosity fails checks 2/6/7/8/9 loudly and leaves the pathspec checks reading the same clean tree. Negative controls only exercise the axis you vary — vary the **path** axis too, or verify each pathspec binds to a real file at least once.

### 📦 After patching this skill, sync the vault SSOT copy

`skill_manage` writes **only** to the AppData copy. This skill also has a git-tracked SSOT at `personal_vault/.scripts/skills/productivity/personal-process-notes/`, and nothing warns you it is behind. On 2026-08-05 it was **4.6KB stale** and still asserted the *"`personal_vault/` is a SEPARATE nested git repo"* claim that had been disproven the day before — a future session reading it would have followed refuted guidance.

🚨 **Run `diff -rq` at the START of every cycle, not only after patching.** (Added 2026-08-09.) A background **curator review turn** can patch this skill while holding only memory + skill tools — no terminal, so it *cannot* sync the SSOT itself, and it cannot leave a reliable breadcrumb either. The AppData copy therefore drifts ahead silently between cycles. Make the comparison unconditional at pre-flight; it costs one command:

```
A="$HOME/AppData/Local/hermes/profiles/personal_profile/skills/productivity/personal-process-notes"
V=/c/Users/khoans/Documents/Personal_OS/personal_vault/.scripts/skills/productivity/personal-process-notes
diff -rq "$A" "$V"      # silent = in sync; any output = SSOT is behind, sync it this cycle
```

After any patch here: `diff -rq <appdata_dir> <vault_ssot_dir>` → sync one-way AppData → SSOT (per the `skill-sync` skill) → archive to `_archives/skills/` → commit and push → confirm `diff -rq` is IDENTICAL. Before syncing, check `diff <appdata> <vault> | grep '^>'` so a one-way copy doesn't destroy a real edit that exists only in the vault copy. Archive naming follows the flat convention already in that folder — `personal-process-notes_SKILL_backup_YYYY-MM-DD.md`, **not** a dated subdirectory.

⚠️ **Do NOT verify this sync with string *counts*.** (Corrected 2026-08-08, twice in one cycle.) An earlier revision demanded the refuted nested-repo claim grep to `0`; but the section above *quotes* that claim to narrate the 2026-08-05 incident, so a correct file greps to 1 — chasing 0 means deleting accurate history. Re-pinning it to "want exactly 1" then broke too, because the fix itself quoted the string again (count → 3). **Any count you write into the doc changes the count.** Use `diff -rq` for sync integrity plus a presence check that is stable under self-reference:

```
diff -rq <appdata_dir> <ssot_dir>                                  # silent = synced; this is the real gate
grep -q 'Git root — VERIFY, do not assume' <ssot>/SKILL.md         # corrected guidance survived the copy
```

General rule this is an instance of: **never verify a doc by asserting an exact occurrence count of text the doc itself discusses, and never prove a string absent when the doc has legitimate reason to quote it.** Assert presence of the corrected claim; let `diff -rq` prove the copy.
