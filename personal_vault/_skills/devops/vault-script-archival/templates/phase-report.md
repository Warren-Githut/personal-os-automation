# Phase N — Archive Report

**Date:** YYYY-MM-DD
**Commit:** <commit-hash>

## Summary
Archived N unused scripts from `vault/scripts/` to `vault/scripts/.archive/YYYY-MM_phaseN/`
- Before: X scripts
- After: Y scripts
- Reduction: Z%

## Archived Files (N)

| # | File | Category | Reason |
|---|------|----------|--------|
| 1 | ... | ... | ... |

## Verification Numbers

| Metric | Expected | Actual | Status |
|--------|----------|--------|--------|
| Active scripts (vault/scripts/) | ~Y | Y | ✅ |
| Archive folder count (N files + 1 README) | N+1 | N+1 | ✅ |
| Git tracked files moved | N | N | ✅ |

## Risk Flags

| File | Risk Level | Notes |
|------|------------|-------|
| ... | HIGH/MEDIUM/LOW | ... |

## Confidence Assessment

**HIGH CONFIDENCE (X/N):**
- List files with reasoning

**MEDIUM CONFIDENCE (Y/N):**
- List files with reasoning

## Rollback Procedure

**Single file:**
```bash
git mv vault/scripts/.archive/YYYY-MM_phaseN/<file> vault/scripts/<file>
```

**All files:**
```bash
git revert <commit-hash>
```

## Archive Location
- Folder: `vault/scripts/.archive/YYYY-MM_phaseN/`
- README: `vault/scripts/.archive/YYYY-MM_phaseN/README.md`
- This report: `vault/_kilo/.archive/PHASE_N_REPORT.md`