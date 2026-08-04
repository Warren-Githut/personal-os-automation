# vault/.scripts/ — SSOT path convention for warren-profile cron/parser scripts

**Class-level lesson (2026-07-23, COL cron rebuild):** the cron pipeline for COL
(`col_*.py`, `col_queue_handler.py`, `ops_col.py`) lives in `vault/.scripts/` (dotfolder,
hidden from Obsidian + `search_files`). The old `vault/scripts/` (no dot) does NOT exist and
is a **stale path trap**.

## The trap
- `ops_col.py` SSOT = `vault/.scripts/ops_col.py` (git-tracked in `warren-os-lusine` repo).
- `col_queue_handler.approve_col()` previously called `VAULT_ROOT / "scripts" / "ops_col.py"`
  → FileNotFoundError at runtime → Warren "ok" appended NOTHING (silent BLOCKER).
- Fix: `VAULT_ROOT / ".scripts" / "ops_col.py"`.

## Rules (durable)
1. **SSOT = `vault/.scripts/`** for all vault parser/cron scripts. NEVER write `vault/scripts/`.
2. **Cron runtime copy = `<profile>/scripts/`** (gitignored in profile repo → force-add).
   Cron resolver only reads from there (see §1 of SKILL.md). It does NOT read `vault/.scripts/`
   directly — so after editing SSOT you MUST re-copy to `<profile>/scripts/`.
3. **`search_files` + `read_file` cannot see dotfolders** (`.scripts/`) on Windows MSYS.
   Use `terminal` `ls`/`grep` to inspect SSOT scripts. Concluding "file missing" from
   `search_files` empty = false negative (Warren-memory pitfall).
4. **Subprocess targets must match the SSOT path.** Any `subprocess.run([..., "ops_col.py", ...])`
   or `importlib` load must point at `vault/.scripts/`, not `vault/scripts/`.
5. **Hardcode `VAULT_ROOT`** in no_agent scripts (cron CWD = `<profile>/scripts/`, so
   `Path(__file__).resolve().parents[N]` resolves WRONG — to profile/, not vault/).

## Verify after any SSOT path change
```bash
# target exists?
test -f vault/.scripts/ops_col.py && echo OK
# old broken path must NOT exist
test -f vault/scripts/ops_col.py && echo "BUG: stale path exists" || echo "good (missing)"
# runtime copy matches SSOT (md5)
md5sum vault/.scripts/col_X.py <profile>/scripts/col_X.py
python3 -m py_compile vault/.scripts/*.py
```

## Related
- `cron-job-ops` SKILL.md §1 (resolver), §3 (gitignore + force-add), §6 (fix procedure).
- `ops-col-cron-automation` skill (2026-07-23, merged 2026-07-25) — full COL cron architecture + pitfalls incl. this.
- `ops-col` skill (PINNED — stale `vault/scripts/` references NOT yet patched; needs
  `hermes curator unpin ops-col` before fix). Flag to Warren.
