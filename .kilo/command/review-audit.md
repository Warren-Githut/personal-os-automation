---
model: deepseek-obsidian/deepseek-v4-pro
description: "Code review & system audit for Personal OS vault (Markdown + Python). Single-file quality review + multi-file cross-reference integrity audit."
updated: 2026-06-02
---

# /review-audit — Code Review & System Audit (Personal OS)
# v2.0-personal | 2026-06-02
# PREVIOUSLY: v1.0 stub
# KEY CHANGES v1.0→v2.0-personal:
#   - Full protocol ported from Warren_OS_Local review-audit v2.0
#   - All content translated to English
#   - Adapted paths: personal_vault/ instead of vault/
#   - System coherence checks target Personal_OS structure (10_PULSE/, wiki/trading/, etc.)
# PURPOSE: After ORION writes code/script for Personal OS → 3 experts review single-file quality → if multi-file, run system coherence audit → Senior QA Manager verdict: SHIP / CONDITIONAL SHIP / REWORK.
# SCOPE: Any script/parser/command ORION writes for Personal OS vault (Python + Markdown protocols). Single-file review + multi-file cross-reference integrity.
# COMPANION: Use after /review-plan (plan first → code after → review-audit before ship).
# TWO MODES: (1) Single file: /review-audit [file] — like old /review-code. (2) System audit: /review-audit — auto-detects recent git changes, runs coherence checks.

---

## Usage

**Mode 1 — Single file review:**
```
/review-audit [path/to/file.py]
/review-audit [paste code to review]
```

**Mode 2 — System coherence audit (auto-detects recent git changes):**
```
/review-audit
```

**Examples:**
```
/review-audit scripts/fetch_stock.py
/review-audit .kilo/command/ingest.md
/review-audit [paste function just written]
/review-audit               # system-wide audit on all recent changes
```

---

## Core Philosophy (mandatory application — no exceptions)

Before reviewing, all 3 experts read and apply these principles:

1. **Clarity over cleverness:** Code that runs = necessary condition. Code that someone else can understand after 6 months = sufficient condition. Don't use exotic tricks to save a few lines.

2. **Single Responsibility:** One function does exactly one thing. If explaining a function's purpose requires using "AND" — that's a mandatory signal to split it.

3. **No Premature Optimization:** Write correct, write clean, make it work first. Only optimize performance when you have measurement data pointing to a specific bottleneck.

4. **Maintainability first:** Write code as if the person maintaining it later is a cold-blooded killer who knows your address. Clear naming, clear error messages, no hidden hardcoding.

5. **Design for Deletion:** Write independent modules like Lego blocks — each block does exactly one thing, no implicit dependencies on other blocks. When requirements change, pull out one block and replace it without collapsing the whole system. Test question: "If I delete this function/module, how many other places break?"

---

## Protocol — 5 Steps, no skip

> **SILENT MODE:** Run Steps 1–4 as internal reasoning — do not print. SILENT MODE overrides all "Required Output:" in Steps below. Sole exception: if you need to ask Warren for clarification → ask before continuing. Only print Step 5 verdict block.

---

### STEP 1 — INTAKE (SILENT)

**Mode 1 — Single file:** ORION reads the specified file/pasted code.

**Mode 2 — System audit (no argument):** ORION auto-detects recent git changes (`git diff --name-status HEAD~1` or `git diff --name-status --cached` if staged). Read all changed files. If count >10 files → priority: command files (.kilo/command/*.md) → index files (AGENTS.md, *_INDEX.md, *_Hub.md) → content files (wiki, pulse, cases) → scripts.

Internal intake (single file):
```
FILE        : [path or "pasted snippet"]
LANGUAGE    : [Python / Markdown / Bash / other]
WHAT IT DOES: [3 lines max — what does this code do, what is input, what is output]
LINE COUNT  : [n lines]
```

Internal intake (batch — system audit):
```
MODE        : SYSTEM AUDIT
FILES       : [n files changed]
  - [file1] : [type — command / index / wiki / script / log]
  - [file2] : [type]
  - ...
SCOPE       : [summary — what does this change do overall]
```

If unclear what the code does after reading → ask Warren 1 question before continuing.
If clear enough → proceed immediately.

---

### STEP 2 — CODE REVIEW 🟦 (SILENT)
*(Senior Engineer — 30 years — reads code as the person who will maintain it)*

Read all code. Evaluate by all 5 lenses of Core Philosophy.

Internal structure:

```
[CR] VIOLATIONS:
  - Line [n]: [what violation] → [why it is a problem]
  - Line [n]: ...
  (If no violation → write "NONE FOUND" — do not leave blank)

[CR] NAMING AUDIT:
  - Any variable/function name that doesn't self-explain? → suggest replacement
  (If OK → "PASS")

[CR] SINGLE RESPONSIBILITY CHECK:
  - Any function doing >1 thing? → point specifically, suggest how to split
  - Hard gate: function >40 lines → mandatory refactor flag (no exceptions)
  (If OK → "PASS")

[CR] DESIGN FOR DELETION CHECK:
  - Any module/function implicitly coupled (changing one requires changing the other)?
  - If function X is deleted, how many other places break? → list them
  - Any hidden dependency not declared at the top of file/function?
  (If OK → "PASS — modules independent, deletion-safe")

[CR] CLARITY SCORE: [1–5]
  1 = must read 3 times to understand | 5 = read once, understand immediately
  Reason: [1 sentence]

[CR] SUGGESTED REFACTOR:
  [Only what is truly needed — no over-engineering. If none → write "NONE"]
```

---

### STEP 3 — STRESS TEST 🟥 (SILENT)
*(QA Engineer — 30 years — specializes in breaking code)*

Don't trust code works until proven.
Write **at least 3 test cases**. Do not skip any of the 3 mandatory types:

```
CASE 1 — Happy Path (normal input, correct format)
  Input   : [specific description]
  Expected: [correct output]
  Verdict : PASS / FAIL / UNKNOWN (needs actual execution)
  Risk if wrong: [consequence if fails — minor / serious / silent]

CASE 2 — Edge Case (valid but unusual input)
  Input   : [example: 0 value, empty string, 28-day month, Vietnamese characters]
  Expected: [correct output]
  Verdict : PASS / FAIL / UNKNOWN
  Risk if wrong: [consequence]

CASE 3 — Failure / Adversarial (wrong input, missing, or malicious)
  Input   : [example: file doesn't exist, .env missing key, API offline, negative number]
  Expected: [code must FAIL LOUDLY — clear error message, no silent crash]
  Verdict : PASS / FAIL / UNKNOWN
  Risk if wrong: [if fails silently, what is the consequence for Warren]

[CASE 4+ if additional critical scenarios found — no limit on count]
```

After all cases:
```
[QA] SILENT FAILURE RISK: [HIGH / MED / LOW] — [1 sentence reason]
  (Silent failure = code runs without error but output is wrong — most dangerous)

[QA] OVERALL TEST VERDICT: [n PASS / n FAIL / n UNKNOWN]
```

**BATTLE TEST CHECK** (auto — don't ask Warren):

Scan code for these patterns:
- File-writing: `open(..., 'w')`, `open(..., 'a')`, `prepend`, `append`, writing to `.md` / `.json`, `Write tool`, `Edit tool`, `write_to_file()`, `apply_diff()`, `prepend_to_file`
- API call: `requests.`, `slack_client`, `gspread`, `calendar`, `WebFetch`, MCP tool call

If NO patterns found → skip this block entirely.

If AT LEAST 1 pattern found:
```
[QA] BATTLE TEST RECOMMENDED:
  Reason: [file-writing / API call] — stress test cannot detect [race condition / rate limit / file lock] during real execution.

  Run this command to verify (PowerShell — 1 command, no setup):
  > [specific command — e.g.: python scripts/fetch_stock.py]

  Run [n] times consecutively to test concurrency:
  > 1..3 | ForEach-Object { Start-Job { python scripts/fetch_stock.py } } | Wait-Job

  Expected: [what Warren should see if correct]
  Red flag: [failure signal — e.g.: corrupt file, duplicate entry, API 429 error]

  → This is OPTIONAL — does not block SHIP. Run when Warren has time.
```

**DRY-RUN CHECK** (mandatory for Python executables — auto, don't ask Warren):

If the code under review is a **Python script that can execute** (has `if __name__ == "__main__"` or CLI entry point):
→ ORION must run dry-run with sample data or `--dry-run` flag before verdict, unless:
  - Script needs input file that doesn't exist yet (first-run), OR
  - Script calls API with rate limit / real side-effect (GSheet write, Slack message)

```
[QA] DRY-RUN RESULT:
  Command    : [command that was run — python <script> <args>]
  Status     : OK / ERROR
  Output     : [summary output — if long, put in artifact]
  Red flags  : [if any — Unicode error, missing import, wrong path]
```

If Dry-run FAIL → prepend `[DRY-RUN FAIL]` to review and suggest fix immediately.
If Dry-run PASS → consider stress test verified by real execution.

**PROTOCOL LOGIC CHECK** (mandatory for Markdown command files — auto, don't ask Warren):

If the code under review is a **Markdown command/protocol file** (`.kilo/command/*.md` or `.md` defining a flow):
→ ORION must trace the entire flow before verdict. Do not skip.

```
[QA] PROTOCOL LOGIC TRACE:
  Flow map  : [linear summary — START → A → B → ... → END]
  Branches  : [n] — where each branch leads (note terminal state)

[QA] DEAD END CHECK:
  - Any branch leading to an undefined state?
  (If not → "PASS — all branches terminate explicitly")

[QA] CIRCULAR REFERENCE CHECK:
  - Any infinite loop? (A → B → A without exit condition)
  (If not → "PASS — no infinite loops")

[QA] STALE REFERENCE CHECK:
  - Any reference to a feature/function that has been deleted/deprecated?
  - Scan for: old gate names, old tools, deprecated flags
  (If not → "PASS — no stale references")

[QA] GATE INTEGRITY CHECK:
  - Each gate has: clear input, decision point, "yes" path, "no" path?
  - Any gate missing a "no" path → flag CRITICAL (user gets stuck)
  (If all pass → "PASS — all gates have complete yes/no paths")
```

If Protocol Logic Trace detects CRITICAL issue (dead end, infinite loop, gate missing "no" path) → auto-downgrade verdict to REWORK.
If only non-critical (stale reference, wording) → flag in NON-CRITICAL ISSUES.

**SYSTEM COHERENCE CHECK** (only triggers in Mode 2 — batch/system audit with ≥2 files changed — auto, don't ask Warren):

When reviewing ≥2 files changed together, ORION must check cross-reference integrity.

```
[SC] REGISTRATION CHECK:
  - Each new file registered in index/AGENTS.md/ORION.md?
  - Deleted file left orphan references in index?
  - Scan: AGENTS.md, ORION.md, *_INDEX.md, *_Hub.md, index.md
  (If pass → "PASS — all new files registered, no orphan references")

[SC] SOURCE ALIGNMENT:
  - Command files (.kilo/command/*.md) claim N sources → actual count of sources listed?
  - Source count mismatch? → flag (claim 9 but list 8, or claim 10 but list 11)
  - Source paths actually exist? (check file existence)
  (If pass → "PASS — source counts match, all paths exist")

[SC] COMPLEMENT FLOWS:
  - File A references "data from file B" → does file B actually output data for A?
  - Complement pairs (e.g.: weekly-connections → context-update): check bidirectional
  - If A claims B feeds into it but B does not mention A → flag MISALIGNMENT
  (If pass → "PASS — all complement flows are bidirectional")

[SC] DOMAIN MAPPING:
  - Wiki files: domain tag in YAML frontmatter matches the folder it's in?
  - Command files: domain list matches WIKI_INDEX.md hub structure?
  - Missing domains? (e.g.: command lists 8 domains but wiki has 9)
  (If pass → "PASS — domains consistent across commands and wiki structure")

[SC] INDEX COMPLETENESS:
  - WIKI_INDEX.md, PULSE_INDEX.md, ACTIVE_CASES_INDEX.md: listing every file in corresponding directory?
  - New files in wiki/ or 10_PULSE/ have entry in index?
  - Deleted/renamed files updated in index?
  (If pass → "PASS — all indexes up to date")

[SC] CROSS-FILE STALE REFERENCES:
  - Scan all changed files for [[wikilink]] or [text](path) references
  - Each reference → does target file exist?
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

If FRAGMENTED → auto-downgrade verdict 1 level (SHIP → CONDITIONAL SHIP, CONDITIONAL SHIP → REWORK).
If MINOR GAPS → flag in NON-CRITICAL ISSUES, do not block SHIP.

---

### STEP 4 — MAINTAINABILITY AUDIT 🟩 (SILENT)
*(Legacy Code Survivor — 30 years — reads code as the person maintaining it 6 months later)*

```
[MA] SINGLE POINTS OF FAILURE:
  - [Where changing 1 line breaks the whole flow — list specifically]
  (If none → "NONE FOUND")

[MA] DELETION SAFETY AUDIT:
  - If Warren needs to remove/replace 1 feature after 6 months → how many files/functions get touched?
  - Are modules truly independent, or implicitly coupled?
  - Suggest module splitting if needed: [module A should split into A1 + A2 because reason X]
  (If OK → "PASS — deletion-safe, modules independent")

[MA] CONFIG FRAGILITY:
  - Warren needs to change 1 config (e.g.: GSheet tab name) → how many places? [n places]
  - Any hidden hardcoded values? → list them
  (If OK → "PASS — all config via .env or parameters")

[MA] ERROR MESSAGES:
  - [GOOD / NEEDS WORK]
  - Example current error message: "[copy from code]"
  - Suggestion: "[clearer version Warren can understand immediately]"
  (If no error handling → flag CRITICAL)

[MA] DEPENDENCY MAP:
  - External: [list file, API, service this code depends on]
  - Assumed state: [what does code assume is true without checking?]

[MA] MAINTAINABILITY SCORE: [1–5]
  1 = only the original author understands | 5 = even Warren can read and understand
  Reason: [1 sentence]
```

---

### STEP 5 — REVIEW-AUDIT VERDICT 🏁

Read all findings from Steps 2–4. No bias. Do not pass code with CRITICAL issues.
If system audit (Mode 2) → integrate SYSTEM COHERENCE CHECK into verdict.

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
REVIEW-AUDIT VERDICT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

MODE       : [SINGLE FILE / SYSTEM AUDIT]
DECISION   : 🟢 SHIP / 🟡 CONDITIONAL SHIP / 🔴 REWORK

CRITICAL ISSUES    : [n] — [list, each 1 line — line number + problem]
NON-CRITICAL ISSUES: [n] — [list]
SILENT FAILURE RISK: [HIGH / MED / LOW]
DELETION SAFETY    : [SAFE / AT RISK] — [1 sentence reason]

TEST RESULTS: [n PASS] / [n FAIL] / [n UNKNOWN]
  Failed cases: [list case names]

MAINTAINABILITY: [score 1-5] | CLARITY: [score 1-5]

SYSTEM COHERENCE: [COHERENT / MINOR GAPS / FRAGMENTED] (only if MODE = SYSTEM AUDIT)
  Issues: [list findings from SC check — if any]

CONDITIONS TO SHIP: (if CONDITIONAL — max 3, specific)
  1. Fix [problem] at [line/function] → do this: [clear instruction]
  2. ...
  3. ...

OPEN QUESTIONS: (only if truly ambiguous before ship — skip if clear)
  [Question] → RECOMMENDED: [answer] | No-friction: [1 sentence] | Long-term: [1 sentence] | Trade-off: [1 sentence]

CONFIDENCE TO SHIP: [HIGH / MOD / LOW] — [1 sentence reason]

SUGGESTED NEXT STEP: [1 single action — what Warren does next]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**SHIP** = no CRITICAL issues, no test FAIL, LOW silent failure risk, maintainability ≥ 3/5, coherence not FRAGMENTED
**CONDITIONAL SHIP** = has issues but quick to fix — list max 3 conditions
**REWORK** = has CRITICAL issue affecting correctness, HIGH silent failure risk, or coherence FRAGMENTED — must rewrite before ship

---

### AFTER SHIP — AUTO-FIX NON-CRITICAL ISSUES

If verdict is SHIP or CONDITIONAL SHIP and there are NON-CRITICAL issues:
→ ORION **auto-applies fixes** without asking Warren.

**Rules:**
- Only fix NON-CRITICAL issues — do not touch CRITICAL (those → REWORK)
- Only fix if it doesn't change logic/behavior — rename, restructure, add error message, extract constant
- If fix requires judgment call (ambiguous) → ask Warren 1 question before applying
- After fixing → output short diff: `[AUTO-FIXED] line N: [change description]`
- If no NON-CRITICAL issues → skip this section, don't mention

---

### AFTER SHIP — MONITOR TASK (mandatory if SHIP or CONDITIONAL SHIP)

Immediately after SHIP verdict, ORION **must** create 1 task entry in `personal_vault/_inbox/tasks.md` (prepend, newest on top):

```
- [ ] [monitor] [automation name] — check [specific output] before [specific deadline]
      Trigger: [condition that activates automation]
      Expected: [what Warren should see if correct]
      Silent fail check: if no output after [n hours] → [specific action to investigate]
```

**Rules:**
- `[automation name]` = name of just-shipped file/script
- `[deadline]` = earliest time automation can trigger after deploy
- `[silent fail check]` = mandatory — most important line since Warren is non-IT, cannot debug
- Task has **no checkbox** — Warren deletes manually after verifying OK. Intentional: if Warren doesn't delete, task stays as reminder.
- If REWORK → **no monitor task**

**If this feature has a Spec block in `personal_vault/_kilo/memory/project_*.md`** (created by /review-plan):
→ ORION updates field `Status: CODING → DONE` and `Next: —` in that file at SHIP time.
→ No Warren action needed — ORION auto-closes the loop.

### AFTER SHIP — AUTO-COMMIT (mandatory if SHIP)

Immediately after AUTO-FIX + MONITOR TASK (if any):

→ ORION **auto git commits** changes:

1. `git -C personal_vault/ add -A` — stage all changes
2. `git -C personal_vault/ commit -m "feat(impl): [feature name] — /review-audit SHIP"` — commit with description

**Rules:**
- If REWORK → **no** auto-commit. Warren decides when to commit.
- If CONDITIONAL SHIP → only auto-commit after applying condition fixes.
- Commit message format: `feat(impl): [feature name] — /review-audit SHIP`
- If multiple files changed → add bullet in commit body: `- [filename]: [short change description]`
- Do not push — only local commit. Warren pushes when ready.

---

## Anti-patterns (not allowed)

- ❌ Pass code with CRITICAL issue because "it works"
- ❌ Skip any of the 3 mandatory test types (happy / edge / failure)
- ❌ Vague violation: "code is a bit hard to read" → must specify line number + concrete reason
- ❌ Suggested refactor makes code more complex instead of simpler
- ❌ Ignore silent failure — most dangerous error type for Warren (non-IT, cannot debug)
- ❌ CONDITIONAL SHIP with >3 conditions — if more than 3, that is REWORK
- ❌ Open Questions for Warren to answer — ORION must recommend answer immediately
- ❌ Recommend fix that increases complexity — always prefer simplest working solution
- ❌ Skip Deletion Safety — implicitly coupled modules are technical debt accumulating over time

---

## Overall workflow (for code/script/command changes)

```
Code change (parser, script, command protocol, automation)
  │
  ├── New feature (new parser, new script, new automation)?
  │   └── /review-plan  → APPROVE / REJECT
  │           ↓ (after approve)
  │     ORION writes code
  │           ↓
  │     /review-audit   → SHIP / REWORK
  │
  └── Small fix / tweak (<20 lines, 1 file)?
      └── Implement directly → /review-audit → SHIP / REWORK

Content entries (/ingest, /insight, case, journal) — NO review-plan or review-audit needed.
Each content command already has its own internal gate to confirm before write.

Batch changes (multi-file, multi-domain)?
  └── /review-audit (no argument) → auto system coherence audit → SHIP / REWORK
```

---

**v2.0-personal | 2026-06-02 | Full protocol ported from Warren_OS_Local review-audit v2.0. Adapted for Personal_OS vault structure: 10_PULSE/ instead of 10_OPERATION_DATA/, personal wiki domains. All content in English (R4 LANGUAGE MANDATE).**
