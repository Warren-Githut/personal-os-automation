---
model: deepseek-obsidian/deepseek-v4-pro
description: "Code review & system audit for Personal OS vault (Markdown + Python). Single-file quality + multi-file cross-reference integrity."
---

# /review-audit — Code Review & System Audit (Personal OS)
# v1.0 | 2026-05-31 | Adapted from L'Usine review-audit v2.0

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

## Protocol — 5 Steps

SILENT MODE: Steps 1-4 internal, only output Step 5 verdict block.

### STEP 1 — INTAKE (SILENT)

**Mode 1 — Single file:** ORION reads the specified file/pasted code.

**Mode 2 — System audit:** ORION auto-detects recent git changes (git diff --name-status HEAD~1). Read all changed files from personal_vault/. Priority: command files (.kilo/command/*.md) -> index files (AGENTS.md, *_INDEX.md, *_Hub.md) -> content files (wiki, pulse, cases) -> scripts.

### STEP 2 — CODE REVIEW (SILENT)
Senior Engineer reviews by 5 lenses: Clarity, Single Responsibility, No Premature Optimization, Maintainability, Design for Deletion.

### STEP 3 — STRESS TEST (SILENT)
QA Engineer writes 3 minimum cases: Happy Path, Edge Case, Failure/Adversarial.
- BATTLE TEST CHECK for file-writing/API patterns
- PROTOCOL LOGIC CHECK for Markdown command files
- SYSTEM COHERENCE CHECK for multi-file changes (same 6 checks: Registration, Source Alignment, Complement Flows, Domain Mapping, Index Completeness, Cross-File Stale References)

### STEP 4 — MAINTAINABILITY AUDIT (SILENT)
SPOF check, Deletion Safety, Config Fragility, Error Messages, Dependency Map.

### STEP 5 — REVIEW-AUDIT VERDICT

```
REVIEW-AUDIT VERDICT
MODE       : [SINGLE FILE / SYSTEM AUDIT]
DECISION   : [GREEN SHIP / YELLOW CONDITIONAL SHIP / RED REWORK]

CRITICAL ISSUES    : [n]
NON-CRITICAL ISSUES: [n]
SILENT FAILURE RISK: [HIGH / MED / LOW]
DELETION SAFETY    : [SAFE / AT RISK]

TEST RESULTS: [n PASS] / [n FAIL] / [n UNKNOWN]
MAINTAINABILITY: [1-5] | CLARITY: [1-5]
SYSTEM COHERENCE: [COHERENT / MINOR GAPS / FRAGMENTED]

CONDITIONS TO SHIP: (if conditional, max 3)
OPEN QUESTIONS: (if ambiguous)
CONFIDENCE TO SHIP: [HIGH / MOD / LOW]
SUGGESTED NEXT STEP: [1 action]
```

SHIP = no critical, no test FAIL, LOW silent failure risk, maintainability >=3, coherent.
REWORK = critical issue, HIGH silent failure risk, or fragmented coherence.

### POST-SHIP — AUTO-FIX non-critical issues, create monitor task, auto-commit.

---

**v1.0 | 2026-05-31 | Personal_OS adaptation. Same protocol, adapted vault paths.**