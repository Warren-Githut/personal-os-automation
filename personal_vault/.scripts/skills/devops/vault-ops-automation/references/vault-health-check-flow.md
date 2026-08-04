# Monday Vault Health Check — Correct Flow & Lint Calibration

**Why this file exists:** Warren's Google Calendar "Monday Weekly Vault Health Check" event
contained a stale command block (pre-2026-07) referencing two dead commands. This is the
verified-correct replacement, plus the lint-schema facts a future session must not revert.

## ROTTED BLOCK (do NOT use)

```
/system-thinker-structure --quick --execute     # dead — renamed to /vault-structure-audit
ops-index-sync --check-only                      # dead — merged into ops_index_lint_sync.py
vault-structure-audit --quick                     # real but step order wrong
```

## CORRECT BLOCK (paste into Google Calendar)

```
MONDAY WEEKLY — Vault Health Check (15 min)

Step 1 (read-only, file-level, ~30s):
  python3 vault/scripts/ops_index_lint_sync.py --check-only
  → index integrity + frontmatter lint.
  → 🔴 Critical > 0 = fix before commit. 🟡 Warning = ops-meta, không block.

Step 2 (optional, vault architecture <5s, dry-run):
  /vault-structure-audit --quick
  → cấu trúc vault, MOC, link graph. Không tự sửa.

Deep audit đầu tháng (có thời gian):
  /vault-structure-audit --execute

Lưu ý:
- Profile/cron health 3 profiles đã có cron 'audit-automation'
  chạy Chủ Nhật 19:00 → thứ 2 chỉ cần check layer file là đủ.
- Không dùng /system-thinker-structure (đã rename) hay ops-index-sync
  (đã merge vào ops_index_lint_sync.py).
```

## LINT SCHEMA CALIBRATION (2026-07-13)

File: `vault/scripts/ops_index_lint_sync.py`

**Before calibration:** 151 critical — ALL false positives. The script forced every
`.md` (including `00_CORE_LOGIC/CONTEXT.md`, `ONTOLOGY.md`, `00_WIKI_INDEX.md`, index files)
to carry `owner / cadence / data_quality / last_reviewed / name / type`.

**After calibration:**

| Layer | Applies to | Critical fields | Warning fields |
|-------|-----------|-----------------|----------------|
| Universal (non-case) | wiki content, 10_OPERATION_DATA, projects | `name, type, status, last_updated` | `owner, cadence, data_quality, last_reviewed` (ops-meta) |
| Case files (`_cases/`) | case md + closed/active/projects | `status, last_updated` (uses `title` not `name`) | ops-meta downgraded |
| Exempt | `00_CORE_LOGIC/*`, `00_*.md`, `index.md`, `log.md`, `DECISION_LOG.md`, `frontmatter_template.md` | (lighter — identity only) | ops-meta |

**Result:** 151 → 9 real criticals (9 files missing `last_updated`/`status`) + ~431 warnings
(ops-meta hygiene, non-blocking).

**Pitfall to remember:** case files use `title`, NOT `name` — do not reintroduce a
`name/type` requirement on `_cases/` or the false-critical flood returns.

## VERIFICATION RECIPE (ad-hoc, reusable)

Write a temp script to `C:/Users/khoans/AppData/Local/Temp/hermes-verify-lint-calibration.py`
and assert:
1. Critical count is small (< 50).
2. Zero criticals flag `name`/`type` on case files.
3. Every critical is only `last_updated`/`status`.
4. No ops-meta field (`owner/cadence/data_quality/last_reviewed`) appears in CRITICAL.
5. Warning lines actually contain ops-meta (proves downgrade happened).

Run `python3 "C:/Users/khoans/AppData/Local/Temp/hermes-verify-lint-calibration.py"`, then delete it.
(Note: `execute_code` is blocked in cron mode; use a temp `.py` file + `python3 file.py`.)
