---
baseline: true
date: "2026-06-19"
vaults:
  work:
    path: "/c/Users/khoans/Documents/Warren_OS_Local/vault"
    gitkeep: 2
    BOM_files: 32
    trailing_chars_filenames: 1
    scripts_stale_dirs: 1  # scripts/_cases/
    scripts_stale_files: 1  # fix_broken_slugs.py
    case_files_active: 27
    case_files_closed: 0
    CASES_INDEX_entries: 27
    empty_dirs: 5
    vault_root_README: false
  personal:
    path: "/c/Users/khoans/Documents/Stock_OS/stock_vault"
    gitkeep: 8
    BOM_files: 22
    trailing_chars_filenames: 0
    scripts_stale_dirs: 0
    scripts_stale_files: 0
    duplicate_frontmatter_template: true
    case_files_active: 2
    case_files_closed: 0
    CASES_INDEX_entries: 2
    empty_dirs: 3
    vault_root_README: false

profiles:
  warren-profile:
    skills_count: 68
    vault: work
    critical_skills_present:
      - ops-cases, ops-ingest, ops-process-logs, ops-index-sync
      - ops-lint, ops-query, lusine-cases, system-thinker-structure, tidy
  lusine-profile:
    skills_count: 45
    vault: work
    critical_skills_present:
      - ops-cases, ops-ingest, ops-process-logs, ops-index-sync
      - ops-lint, ops-query, lusine-cases, system-thinker-structure, tidy
  personal_profile:
    skills_count: 46
    vault: personal
    critical_skills_present:
      - lusine-cases, system-thinker-structure
    critical_skills_missing:
      - ops-cases, ops-ingest, ops-process-logs, ops-index-sync
      - ops-lint, ops-query, tidy

notes:
  - "personal_profile missing 7/9 ops skills — intentional (personal vault doesn't run ops)"
  - "Both vaults missing root README.md — orientation file absent"
  - "lusine-profile (45 skills) is leaner than warren-profile (68) on same vault"
  - "HORION legacy dir present — not an active profile"
  - "Duplicate frontmatter_template.md in personal vault _cases/active/"