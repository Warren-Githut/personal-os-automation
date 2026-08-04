---
name: qa-gate
description: "Auto-fire: QA execution gate — aggregate verify-parser-output + ab-test (+ battle-test + speckit-converge for qa-full) → single PASS/FAIL verdict before reviewer-node. FAIL = pipeline BLOCKED."
disable-model-invocation: false
version: 1.0.0
author: GG (Hermes)
created: 2026-07-29
trigger: "auto — safenet §D gọi trước khi spawn reviewer-node"
category: core
tags: [qa, gate, testing, quality, pipeline]
related_skills: [verify-parser-output, ab-test, speckit-converge, safenet, reviewer-node]
---

# qa-gate — QA Execution Gate

> **Purpose:** Aggregate test results → single PASS/FAIL verdict. Sits between safenet routing and reviewer-node. FAIL = pipeline blocked, no reviewer-node spawned.

---

## Trigger

Called by `safenet` §D BEFORE spawning `reviewer-node`. Not user-invoked directly.

**Route:** safenet routing table → `qa-gate` → (if PASS) → `reviewer-node`

---

## Zone → Level Mapping (Bố approved 2026-07-29)

| Zone | QA Level | Tests Run | Reviewer-Node After? |
|------|----------|-----------|----------------------|
| 🟢 chat thường | **qa-min** | `verify-parser-output` + `ab-test` | NO |
| 🟡 phân tích | **qa-full** | qa-min + `battle-test` (in ab-test) + `speckit-converge` | YES |
| 🔴 ship/build | **qa-full** | qa-min + `battle-test` (in ab-test) + `speckit-converge` | YES |

> **Note:** `battle-test` is merged into `ab-test` skill (Adversarial Battle Test section). qa-full loads ab-test in full mode.

---

## Execution Sequence

### 🟢 qa-min (3 steps)

```
Step 1: skill_view("verify-parser-output") → run → verdict: PASS/FAIL
Step 2: skill_view("ab-test") → run (basic comparison) → verdict: PASS/FAIL
Step 3: aggregate → PASS (both pass) or FAIL (any fail)
```

**Completion criterion:** Both skills loaded, executed, and verdict captured. At least 1 PASS + 1 PASS = aggregate PASS.

### 🟡/🔴 qa-full (5 steps)

```
Step 1: Run qa-min (verify-parser-output + ab-test basic)
Step 2: IF qa-min FAIL → STOP, skip remaining. Verdict = FAIL.
Step 3: skill_view("ab-test") → run battle-test section → verdict: PASS/FAIL
Step 4: skill_view("speckit-converge") → run → verdict: PASS/FAIL
Step 5: aggregate → PASS (all 4 pass) or FAIL (any fail)
```

**Completion criterion:** All 4 test layers executed (or early-stop on fail). Aggregate verdict captured.

**FAIL-fast rule:** If qa-min fails, do NOT load battle-test or speckit-converge — save token + context.

---

## Verdict Format

### PASS

```
🔰 QA-GATE: ✅ PASS [qa-min] — verify-parser ✓ ab-test ✓
```
or
```
🔰 QA-GATE: ✅ PASS [qa-full] — verify-parser ✓ ab-test ✓ battle-test ✓ speckit-converge ✓
```

### FAIL

```
🔰 QA-GATE: 🔴 FAIL [qa-full] — 2/4 tests failed
   ✅ verify-parser-output: PASS
   🔴 ab-test (battle): FAIL — edge case #3: LU7 covers = 0 at 10h
   ✅ ab-test (basic): PASS
   🔴 speckit-converge: FAIL — missing item from spec §3.2
→ BLOCKED. Reviewer-node NOT spawned. Fix errors → re-run QA.
```

---

## Rules

| # | Rule | Rationale |
|---|------|-----------|
| 1 | **Sequential, NOT parallel** | Each test depends on prior passing. Parallel = wasted token on doomed branch. |
| 2 | **FAIL-fast** | qa-min fail → stop. Don't load heavy tests on dirty artifact. |
| 3 | **FAIL = BLOCKED** | Do NOT spawn reviewer-node. Do NOT ship to Bố. Fix + re-run. |
| 4 | **PASS = proceed** | Safenet continues to reviewer-node (if zone 🟡/🔴). 🟢 zone ends here. |
| 5 | **Clean handoff** | Reviewer-node only sees artifact AFTER QA passes. No test noise in reviewer context. |
| 6 | **`quick:` skip** | Bố prefixes `quick:` → skip entire qa-gate (Bố accepts risk). Gate line: `⚡ no-gate (quick-Q)`. |

---

## Gate Line Integration (SOUL §8)

After PASS → add `qa✓` to `✅ GATES:` line:
```
✅ GATES: boot✓ freeze✓ safenet✓ qa✓ archive✓
```

After FAIL → replace with `qa🔴`:
```
✅ GATES: boot✓ freeze✓ safenet✓ qa🔴 archive✓
```
+ explicit FAIL block above.

---

## Integration Map

```
safenet §D (router)
    │
    ├─ zone 🟢 → qa-gate(qa-min) → PASS → deliver (no reviewer)
    │                               └─ FAIL → BLOCKED
    │
    └─ zone 🟡/🔴 → qa-gate(qa-full) → PASS → reviewer-node → deliver
                                       └─ FAIL → BLOCKED
```

**Called by:** `safenet` §D routing table row "Warren analysis/report (ANY)"

**Calls:** `verify-parser-output`, `ab-test`, `speckit-converge`

**Feeds into:** `reviewer-node` (only if PASS + zone 🟡/🔴)

---

## Pitfalls

- **Skipping qa-gate** → reviewer sees dirty artifact → wastes 2 review rounds catching data errors that verify-parser should have caught. Cost: +5min + extra token.
- **Running tests in parallel** → if verify-parser fails, battle-test ran for nothing. Always sequential, fail-fast.
- **Over-testing 🟢** → qa-min is enough for chat questions. Don't run full battle-test on "LU3 revenue tuần này?".
- **False PASS** → if a test skill returns no verdict (silent), treat as FAIL. No verdict ≠ PASS.
- **Quick-Q bypass** → Bố `quick:` skips QA intentionally. GG still silently verify but doesn't block. Token `⚡` makes bypass visible.
