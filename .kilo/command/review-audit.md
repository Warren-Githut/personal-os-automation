---

description: "Code review & system audit for Warren OS vault (80% Markdown, 20% Python). Single-file quality + multi-file cross-reference integrity. Replaces /review-code."
updated: 2026-06-02
---

# /review-audit — Code Review & System Audit
# v2.0 | 2026-05-27
# PREVIOUSLY: /review-code v1.9
# KEY CHANGES v1.9→v2.0:
#   - RENAMED: /review-code → /review-audit (better fit for 80% Markdown vault)
#   - SYSTEM COHERENCE CHECK: New cross-reference integrity audit for multi-file changes
#   - Step 1: "CODE INTAKE" → "INTAKE" — accepts single file OR batch (N files)
#   - Step 5: "CODE REVIEW VERDICT" → "REVIEW-AUDIT VERDICT"
# PURPOSE: After ORION+Deepseek finishes writing code/script → 3 experts review single-file quality → if multi-file, run system coherence audit → Senior QA Manager verdict: SHIP / CONDITIONAL SHIP / REWORK.
# SCOPE: Any script/parser/command ORION+Deepseek writes for Warren OS vault (Python + Markdown protocols). Single-file review + multi-file cross-reference integrity.
# COMPANION: Use after /review-plan (plan first → code next → review-audit before shipping).
# TWO MODES: (1) Single file: /review-audit [file] — like old /review-code. (2) System audit: /review-audit — auto-detects recent git changes, runs coherence checks.

---

## Usage

**Mode 1 — Single file review:**
```
/review-audit [path/to/file.py]
/review-audit [paste code snippet to review]
```

**Mode 2 — System coherence audit (auto-detects recent git changes):**
```
/review-audit
```

**Examples:**
```
/review-audit scripts/cogs_parser.py
/review-audit .kilo/command/ops-ingest.md
/review-audit [paste function just written]
/review-audit               # system-wide audit on all recent changes
```

---

## Core Philosophy (mandatory — no exceptions)

Before reviewing, all 3 experts read and apply the following philosophy:

1. **Clarity over cleverness:** Working code = necessary condition. Code another person can understand immediately 6 months later = sufficient condition. Don't use exotic tricks to save a few lines.

2. **Single Responsibility:** One function does exactly one thing. If explaining a function requires the word "AND" — that's a mandatory signal to split it apart.

3. **No Premature Optimization:** Write it correct, write it clean, get it running first. Only optimize performance when measurement data points to a specific bottleneck.

4. **Maintainability first:** Code as if the future maintainer is a cold-blooded killer who knows your home address. Clear names, clear error messages, no hidden hardcodes.

5. **Design for Deletion:** Write independent modules like Lego blocks — each block does exactly one thing, no implicit dependency on other blocks. When requirements change, pull one block out and replace it without collapsing the entire system. Test question: "If I delete this function/module, how many other places break along with it?"

---

## Protocol — 5 Steps, no skipping

> **SILENT MODE:** Run Steps 1–4 as internal reasoning — do not print. SILENT MODE overrides all "Required Output:" in the Steps below. Only exception: if clarification from Warren is needed → ask before continuing. Only print Step 5 verdict block.

---

### STEP 1 — INTAKE (SILENT)

**Mode 1 — Single file:** ORION reads the specified file/code snippet.

**Mode 2 — System audit (no argument):** ORION auto-detects recent git changes (`git diff --name-status HEAD~1` or `git diff --name-status --cached` if staged). Reads all changed files. If >10 files → priority: command files (.kilo/command/*.md) → index files (CLAUDE.md, *_INDEX.md, *_Hub.md) → content files (wiki, pulse, cases) → scripts.

Internal intake (single file):
```
FILE        : [path or "pasted snippet"]
LANGUAGE    : [Python / Markdown / Bash / other]
WHAT IT DOES: [max 3 lines — what this code does, what the input is, what the output is]
LINE COUNT  : [n lines]
```

Internal intake (batch — system audit):
```
MODE        : SYSTEM AUDIT
FILES       : [n files changed]
  - [file1] : [type — command / index / wiki / script / log]
  - [file2] : [type]
  - ...
SCOPE       : [summary — what this change does overall]
```

If unclear what the code does after reading → ask Warren 1 question before continuing.
If clear enough → proceed immediately.

---

### STEP 2 — CODE REVIEW 🟦 (SILENT)
*(Senior Engineer — 30 years — reads code like the person who will maintain it)*

Read the entire codebase. Evaluate against exactly the 5 lenses of Core Philosophy.

Internal structure:

```
[CR] VIOLATIONS:
  - Line [n]: [what violation] → [why it's a problem]
  - Line [n]: ...
  (If no violations → clearly state "NONE FOUND" — don't leave blank)

[CR] NAMING AUDIT:
  - Which variables/functions have non-self-explanatory names? → suggest replacement names
  (If fine → "PASS")

[CR] SINGLE RESPONSIBILITY CHECK:
  - Which function is doing >1 thing? → point out specifically, suggest how to split
  - Hard gate: any function >40 lines → mandatory refactor flag (no exceptions)
  (If fine → "PASS")

[CR] DESIGN FOR DELETION CHECK:
  - Which modules/functions are implicitly coupled (changing one forces changes to the other)?
  - If function X is deleted, how many other places break? → list them
  - Any hidden dependencies not explicitly declared at the top of the file/function?
  (If fine → "PASS — modules are independent, deletion-safe")

[CR] CLARITY SCORE: [1–5]
  1 = needs 3 reads to understand | 5 = understood on first read
  Reason: [1 sentence]

[CR] SUGGESTED REFACTOR:
  [Only what's genuinely needed — don't over-engineer. If not needed → write "NONE"]
```

---

### STEP 3 — STRESS TEST 🟥 (SILENT)
*(QA Engineer — 30 years — specializes in breaking code)*

Don't trust code runs correctly until proven.
Write **at least 3 test cases**. Must not skip any of the 3 mandatory types below:

```
CASE 1 — Happy Path (normal input, correct format)
  Input   : [specific description]
  Expected: [what the correct output is]
  Verdict : PASS / FAIL / UNKNOWN (needs actual run)
  Risk if wrong: [consequence if fail — minor / serious / silent]

CASE 2 — Edge Case (valid but unusual input)
  Input   : [example: value 0, empty string, month with 28 days, Vietnamese characters]
  Expected: [what the correct output is]
  Verdict : PASS / FAIL / UNKNOWN
  Risk if wrong: [consequence]

CASE 3 — Failure / Adversarial (wrong, missing, or destructive input)
  Input   : [example: non-existent file, .env missing key, GSheet offline, negative number]
  Expected: [code must FAIL LOUDLY — clear error message, no silent crash]
  Verdict : PASS / FAIL / UNKNOWN
  Risk if wrong: [if fails silently, what is the consequence for Warren]

[CASE 4+ if additional critical scenarios are detected — no limit on quantity]
```

After all cases:
```
[QA] SILENT FAILURE RISK: [HIGH / MED / LOW] — [1 sentence reason]
  (Silent failure = code runs without errors but output is wrong — most dangerous)

[QA] OVERALL TEST VERDICT: [n PASS / n FAIL / n UNKNOWN]
```

**BATTLE TEST CHECK** (automatic — don't ask Warren):

Scan code for the following patterns:
- File-writing: `open(..., 'w')`, `open(..., 'a')`, `prepend`, `append`, write to `.md` / `.json`, `Write tool`, `Edit tool`, `write_to_file()`, `apply_diff()`, `mcp__obsidian__edit`, `prepend_to_file`
- API call: `requests.`, `slack_client`, `gspread`, `calendar`, `WebFetch`, MCP tool call

If NO patterns found → skip this block entirely.

If AT LEAST 1 pattern found:
```
[QA] BATTLE TEST RECOMMENDED:
  Reason: [file-writing / API call] — stress test cannot detect [race condition / rate limit / file lock] in real execution.

  Run the following command to verify (PowerShell — 1 command, no setup needed):
  > [specific command — example: python scripts/cogs_parser.py test_data/sample.txt]

  Run [n] times consecutively to test concurrency (replace command below with actual command of code under review):
  > 1..3 | ForEach-Object { Start-Job { python scripts/cogs_parser.py } } | Wait-Job

  Expected: [output Warren should see if correct]
  Red flag: [sign of failure — example: corrupt file, duplicate entry, API 429 error]

  → This is OPTIONAL — does not block SHIP. Run when Warren has time.
```

**DRY-RUN CHECK** (mandatory for Python executables — automatic, don't ask Warren):

If the code under review is an **executable Python script** (has `if __name__ == "__main__"` or CLI entry point):
→ Claude must run dry-run with sample data or `--dry-run` flag before verdict, unless:
  - Script needs input file that doesn't exist yet (first-run), OR
  - Script calls API with rate limits / real side-effects (GSheet write, Slack message)

```
[QA] DRY-RUN RESULT:
  Command    : [command run — python <script> <args>]
  Status     : OK / ERROR
  Output     : [output summary — if long, put in artifact]
  Red flags  : [if any — Unicode error, missing import, wrong path]
```

If Dry-run FAIL → attach flag `[DRY-RUN FAIL]` at the top of review and suggest fix immediately.
If Dry-run PASS → consider stress test verified in practice.

**PROTOCOL LOGIC CHECK** (mandatory for Markdown command files — automatic, don't ask Warren):

If the code under review is a **Markdown command/protocol file** (`.claude/commands/*.md` or `.md` file defining a flow):
→ ORION must trace the entire flow before verdict. No skipping.

```
[QA] PROTOCOL LOGIC TRACE:
  Flow map  : [linear summary — START → A → B → ... → END]
  Branches  : [n] — where each branch leads (clearly state terminal state)

[QA] DEAD END CHECK:
  - Any branch that leads to an undefined state?
  (If none → "PASS — all branches terminate explicitly")

[QA] CIRCULAR REFERENCE CHECK:
  - Any infinite loops? (A → B → A with no exit condition)
  (If none → "PASS — no infinite loops")

[QA] STALE REFERENCE CHECK:
  - Any references to deleted/deprecated features/functions?
  - Scan for: old gate names, old tools, deprecated flags
  (If none → "PASS — no stale references")

[QA] GATE INTEGRITY CHECK:
  - Does each gate have: clear input, decision point, "yes" path, "no" path?
  - Any gate missing "no" path → flag CRITICAL (user gets stuck)
  (If all pass → "PASS — all gates have complete yes/no paths")
```

If Protocol Logic Trace detects a CRITICAL issue (dead end, infinite loop, gate missing "no" path) → automatically downgrade verdict to REWORK.
If only non-critical (stale reference, wording) → flag in NON-CRITICAL ISSUES.

**SYSTEM COHERENCE CHECK** (only triggers in Mode 2 — batch/system audit with ≥2 files changed — automatic, don't ask Warren):

When reviewing ≥2 files changed simultaneously, ORION must check cross-reference integrity. This is the new part of /review-audit that old /review-code didn't have.

```
[SC] REGISTRATION CHECK:
  - Is each newly created file registered in index/CLAUDE.md/ORION.md?
  - Are deleted files still referenced in the index?
  - Scan: CLAUDE.md, ORION.md, *_INDEX.md, *_Hub.md, index.md
  (If pass → "PASS — all new files registered, no orphan references")

[SC] SOURCE ALIGNMENT:
  - Command files (.kilo/command/*.md) claim N sources → count actual listed sources
  - Source count mismatch? → flag (claim 9 but list 8, or claim 10 but list 11)
  - Do source paths actually exist? (check file existence)
  (If pass → "PASS — source counts match, all paths exist")

[SC] COMPLEMENT FLOWS:
  - File A references "data provided by file B" → does file B actually output data for A?
  - Complement pairs (example: weekly-connections → context-update): check bi-directionally
  - If A claims B feeds into it but B doesn't mention A → flag MISALIGNMENT
  (If pass → "PASS — all complement flows are bidirectional")

[SC] DOMAIN MAPPING:
  - Wiki files: does domain tag in YAML frontmatter match the directory containing it?
  - Command files: does domain list match WIKI_INDEX.md hub structure?
  - Missing domains? (example: command lists 8 domains but wiki has 9)
  (If pass → "PASS — domains consistent across commands and wiki structure")

[SC] INDEX COMPLETENESS:
  - WIKI_INDEX.md, OPERATION_INDEX.md, ACTIVE_CASES_INDEX.md: do they list every file in the corresponding directory?
  - New file created in wiki/ or 10_OPERATION_DATA/ — does it have an entry in the index?
  - Deleted/renamed file — has the index been updated?
  (If pass → "PASS — all indexes up to date")

[SC] CROSS-FILE STALE REFERENCES:
  - Scan all changed files for [[wikilink]] or [text](path) references
  - Each reference → does the target file exist?
  - Stale reference to deleted/renamed file? → flag
  (If pass → "PASS — no stale cross-references")
```

**Coherence verdict:**
```
[SC] OVERALL COHERENCE: [COHERENT / MINOR GAPS / FRAGMENTED]
  - COHERENT = 0 issues, all checks pass
  - MINOR GAPS = 1-2 non-critical findings (missing index entry, wording mismatch)
  - FRAGMENTED = ≥3 issues or 1 critical finding (stale ref, broken complement flow)
```

If FRAGMENTED → automatically downgrade verdict 1 level (SHIP → CONDITIONAL SHIP, CONDITIONAL SHIP → REWORK).
If MINOR GAPS → flag in NON-CRITICAL ISSUES, don't block SHIP.

---

### STEP 4 — MAINTAINABILITY AUDIT 🟩 (SILENT)
*(Legacy Code Survivor — 30 years — reads code like the maintainer 6 months later)*

```
[MA] SINGLE POINTS OF FAILURE:
  - [Where changing 1 line breaks the entire flow — list specifically]
  (If none → "NONE FOUND")

[MA] DELETION SAFETY AUDIT:
  - If Warren needs to remove/replace a feature 6 months later → how many files/functions must be touched?
  - Are modules truly independent, or implicitly coupled?
  - Suggest module split if needed: [module A should split into A1 + A2 because reason X]
  (If fine → "PASS — deletion-safe, modules are independent")

[MA] CONFIG FRAGILITY:
  - Warren needs to change 1 config (example: GSheet tab name) → must change in how many places? [n places]
  - Any hidden hardcoded values? → list them
  (If fine → "PASS — all config via .env or parameters")

[MA] ERROR MESSAGES:
  - [GOOD / NEEDS WORK]
  - Current error message example: "[copy from code]"
  - Suggestion: "[clearer version for Warren to understand immediately]"
  (If no error handling → flag as CRITICAL)

[MA] DEPENDENCY MAP:
  - External: [list files, APIs, services this code depends on]
  - Assumed state: [what does the code assume is true without checking?]

[MA] MAINTAINABILITY SCORE: [1–5]
  1 = only the author understands | 5 = Warren reading it also understands
  Reason: [1 sentence]
```

---

### STEP 5 — REVIEW-AUDIT VERDICT 🏁

Read all findings from Steps 2–4. No bias. No passing code with CRITICAL issues.
If system audit (Mode 2) → integrate SYSTEM COHERENCE CHECK into verdict.

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
REVIEW-AUDIT VERDICT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

MODE       : [SINGLE FILE / SYSTEM AUDIT]
DECISION   : 🟢 SHIP / 🟡 CONDITIONAL SHIP / 🔴 REWORK

CRITICAL ISSUES    : [n] — [list, 1 item per line — line number + issue]
NON-CRITICAL ISSUES: [n] — [list]
SILENT FAILURE RISK: [HIGH / MED / LOW]
DELETION SAFETY    : [SAFE / AT RISK] — [1 sentence reason]

TEST RESULTS: [n PASS] / [n FAIL] / [n UNKNOWN]
  Failed cases: [list case names]

MAINTAINABILITY: [score 1–5] | CLARITY: [score 1–5]

SYSTEM COHERENCE: [COHERENT / MINOR GAPS / FRAGMENTED] (only shown if MODE = SYSTEM AUDIT)
  Issues: [list findings from SC check — if any]

CONDITIONS TO SHIP: (if CONDITIONAL — max 3, specific)
  1. Fix [issue] at [specific line/function] → do this: [clear instruction]
  2. ...
  3. ...

OPEN QUESTIONS: (only appears if there's genuinely an ambiguous point before shipping — skip if clear)
  [Question] → RECOMMENDED: [answer] | No-friction: [1 sentence] | Long-term: [1 sentence] | Trade-off: [1 sentence]

CONFIDENCE TO SHIP: [HIGH / MOD / LOW] — [1 sentence reason]

SUGGESTED NEXT STEP: [1 single action — what Warren does next]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**SHIP** = no CRITICAL issues, no FAIL test cases, silent failure risk LOW, maintainability ≥ 3/5, coherence not FRAGMENTED
**CONDITIONAL SHIP** = has issues but quickly fixable — list max 3 conditions
**REWORK** = has CRITICAL issue affecting correctness, silent failure risk HIGH, or coherence FRAGMENTED — must rewrite before shipping

---

### AFTER SHIP — AUTO-FIX NON-CRITICAL ISSUES

If verdict is SHIP or CONDITIONAL SHIP and there are NON-CRITICAL issues in the list:
→ Claude **applies fixes immediately** without asking Warren.

**Rules:**
- Only fix NON-CRITICAL issues — don't touch CRITICAL (those → REWORK)
- Only fix if fix doesn't change logic/behavior — rename, restructure, add error message, extract constant
- If fix needs judgment call (ambiguous) → ask Warren 1 question before applying
- After fixing → output short diff: `[AUTO-FIXED] line N: [change description]`
- If no NON-CRITICAL issues → skip this section, don't mention

---

### AFTER SHIP — MONITOR TASK (mandatory if SHIP or CONDITIONAL SHIP)

Right after SHIP verdict, Claude **must** create 1 task entry in `_inbox/tasks.md` (prepend, newest on top):

```
- [ ] [monitor] [automation name] — check [specific output] before [specific deadline]
      Trigger: [automation trigger condition]
      Expected: [output Warren should see if correct]
      Silent fail check: if output not seen after [n hours] → [specific action to investigate]
```

**Rules:**
- `[automation name]` = file/script name just shipped
- `[specific output]` = Claude auto-generates based on reviewed code — don't hardcode generic
- `[deadline]` = earliest time automation could trigger after deploy (example: "7:00am tomorrow" for morning brief, "next process-notes run" for watcher)
- `[silent fail check]` = mandatory — this is the most important line because Warren is non-IT, can't debug
- This task **has no checkbox** — Warren deletes manually after verifying it's fine. This is intentional: if Warren doesn't delete, the task remains as a reminder.
- If REWORK → **don't create monitor task**

**If this feature has a Spec block in memory/project_*.md** (created by /review-plan):
→ Claude updates field `Status: PLANNING/CODING → DONE` and `Next: —` in that file immediately at SHIP.
→ Warren doesn't need to do anything — Claude auto-closes the loop.

### AFTER SHIP — AUTO-COMMIT (mandatory if SHIP)

Right after completing AUTO-FIX + MONITOR TASK (if any):

→ Claude **auto git commits** changes:

1. `git add -A` — stage all changes
2. `git commit -m "feat(impl): [feature name] — /review-audit SHIP"` — commit with descriptive message

**Rules:**
- If REWORK → **don't** auto-commit. Warren decides when to commit.
- If CONDITIONAL SHIP → only auto-commit after conditions have been fixed.
- Commit message format: `feat(impl): [feature name] — /review-audit SHIP`
- If many files changed → add bullets in commit body: `- [file name]: [short change description]`
- Don't push — only local commit. Warren pushes when desired.

---

## Anti-patterns (do not do)

- ❌ Pass code with CRITICAL issue because "it runs"
- ❌ Skip any of the 3 mandatory test case types (happy / edge / failure)
- ❌ Vague violation: "code is a bit hard to read" → must point to line number + specific reason
- ❌ Suggested refactor makes code more complex instead of simpler
- ❌ Skip silent failure — this is the most dangerous error type for Warren (non-IT, can't debug)
- ❌ CONDITIONAL SHIP with >3 conditions — if more than 3, it's REWORK
- ❌ Open Questions for Warren to answer himself — Claude must recommend answer immediately
- ❌ Recommend fix that increases complexity — always prioritize simplest solution that works
- ❌ Skip Deletion Safety — implicitly coupled modules are technical debt that accumulates over time

---

## Overall Workflow (for code/script/command changes)

```
Code change (parser, script, command protocol, automation)
  │
  ├─ New feature (new parser, new script, automation)?
  │   └─ /review-plan  → APPROVE / REJECT
  │           ↓ (after approval)
  │     ORION+Deepseek writes code
  │           ↓
  │     /review-audit   → SHIP / REWORK
  │
  └─ Small fix / tweak (<20 lines, 1 file)?
      └─ Implement directly → /review-audit → SHIP / REWORK

Content entries (/ops-ingest, /ops-insight, case, journal) — do NOT need review-plan or review-audit.
Each content command already has its own internal gate for confirmation before writing.

Batch changes (multi-file, multi-domain)?
  └─ /review-audit (no argument) → auto system coherence audit → SHIP / REWORK
```

---

**v2.0 | 2026-05-27 | Renamed /review-code → /review-audit. Added SYSTEM COHERENCE CHECK for multi-file batch audits (6 checks: registration, source alignment, complement flows, domain mapping, index completeness, cross-file stale references). Step 1 renamed INTAKE with batch mode. Step 5 renamed REVIEW-AUDIT VERDICT with coherence integration. v1.9 added PROTOCOL LOGIC CHECK for Markdown command files.**
