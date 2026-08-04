# Test Harness Reference — Personal_OS Vault

## What actually runs tests here

The vault is a **personal knowledge vault**, not a JS project. Two test mechanisms exist:

### 1. pytest (REAL, runnable)
- Location: `tests/test_process_sleep.py` (+ `tests/__pycache__/`, `.pytest_cache/`)
- Covers: `capture-sleep` logic — duration parsing (`TestParseDuration`), multi-log parsing (`TestParseAllSleepLogs`), duplicate-key detection (`TestDuplicateKey`, `TestIsDuplicate`), BP insight generation (`TestGenerateInsight`, `TestBuildEntry`).
- Run: `python3 -m pytest tests/ -q`
- Latest known state: **18 passed in ~0.03s** (verified 2026-07-10).
- Scope limit: covers ONLY sleep-log parsing. Does NOT exercise `/process-notes` orchestration, inbox routing, or gap detection.

### 2. npm run test (DUMMY — ignore)
- `package.json` `scripts.test` = `echo "Error: no test specified" && exit 1`
- Always exits 1. No `node_modules/`, no real JS tests.
- The agent runtime may nag "run npm run test" after any file edit — this is a false signal for this vault. Do not run it to "verify"; it will always fail regardless of repo state.

## Why this matters for /process-notes
- The orchestrator touches data files (`.last_process_notes`, `log.md`) — these need only the 6 manual checks in SKILL.md §Verification.
- If a session also edits skill CODE (e.g. patches `capture-sleep`, `personal-inbox-routing`, or adds a new parsing helper), run `pytest tests/` to confirm sleep parsing still passes.
- Never claim "verified via npm run test" — it is non-functional by design.
