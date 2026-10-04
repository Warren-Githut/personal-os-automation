# Cleanup Report Template — Archival Folder Removal

## Usage
Copy this template, fill in bracketed fields, save as `vault/_kilo/.archive/CLEANUP_<FOLDER>_REPORT.md`.

---

# Cleanup Report — .archive/<folder>/

## Date: YYYY-MM-DD

## Action
git rm -r .archive/<folder>/ (N files)

## Commit hash
<git commit hash>

## Files removed
- file1.md
- file2.md
- ...

## Reference docs still mention archived commands
- vault/00_CORE_LOGIC/CONTEXT.md
- vault/RULES.md
Note: References are documentation, not execution. Broken doc links possible but not breaking workflow.

## Risk: LOW
## Confidence: HIGH
## Rollback: git revert <hash>