---
name: cron-silent-failure-scan
description: "Scan cron scripts for silent-failure code patterns."
category: devops
tags: ["audit", "cron", "silent-failure", "code-scan"]
version: 1.0.0
author: Hermes
triggers:
  - "check cron có con nào chết không"
  - "audit cron silent failure"
  - "scan script except pass"
related_skills: ["audit-automation", "cron-job-ops", "luso-parsers"]
---

# cron-silent-failure-scan — Silent Failure Code Audit

> **Purpose:** `cronjob list` hiển thị `last_status` nhưng không phát hiện pattern code nuốt lỗi âm thầm. Scan này chạy bổ sung cho `audit-automation` Step 1b để phát hiện 4 class lỗi câm trong Python scripts.

## When to Use

- Warren asks "check cron có con nào chết không" / "có script nào fail âm thầm không"
- After deploying new cron scripts — verify no swallowed errors
- Weekly audit (pair with `audit-automation`)
- After copying code between similar scripts (risk of dropped functions like `_token()`)

---

## 4 Scan Patterns

### 1. SWALLOWED ERROR — `except: pass`

```bash
grep -rn "except:" --include="*.py" . | grep -v ".archive/" | grep -v "__pycache__" | grep -E "except\s*:\s*pass\s*$"
```

**Risk:** 🔴 CRITICAL trong data path. Exception bị nuốt → script exit 0 dù thất bại.
**Low risk:** `except: pass` trong `finally` block (cleanup temp file).

### 2. DANGEROUS FALLBACK — `return 0` / `return ""` sau except

```bash
grep -rn "return 0\|return \"\"" --include="*.py" . | grep -v ".archive/" | grep -v "__pycache__" | grep -i "except"
```

**Risk:** 🟡 WARNING. Parse fail → trả giá trị "an toàn" giả → số liệu sai âm thầm.

### 3. PROPAGATION GAP — `sys.exit(0)` trong except block

```bash
grep -rn "sys.exit(0)" --include="*.py" . | grep -v ".archive/" | grep -v "__pycache__"
```

**Risk:** 🔴 CRITICAL nếu trong except block của cron script (fail nhưng exit 0 → cron thấy OK).
**Low risk:** `sys.exit(0)` ở CLI usage error (không phải cron).

### 4. FALSE GREEN — `last_status=ok` nhưng script đã xóa

Cross-check `cronjob list` → extract no_agent scripts → verify file exists on disk.

**Risk:** 🔴 CRITICAL. Cron báo OK nhưng script không tồn tại → `last_status` là stale.

---

## Execution Recipe

```bash
VAULT_SCRIPTS="/c/Users/khoans/Documents/Warren_OS_Local/vault/.scripts"

# === SCAN 1: Swallowed Errors ===
echo "=== SWALLOWED ERRORS ==="
cd "$VAULT_SCRIPTS"
grep -rn "except:" --include="*.py" . | grep -v ".archive/" | grep -v "__pycache__" | grep -E "except\s*:\s*pass\s*$"

# === SCAN 2: Dangerous Fallbacks ===
echo "=== DANGEROUS FALLBACKS ==="
grep -rn "return 0\|return \"\"" --include="*.py" . | grep -v ".archive/" | grep -v "__pycache__" | grep -i "except"

# === SCAN 3: Propagation Gaps ===
echo "=== PROPAGATION GAPS ==="
grep -rn "sys.exit(0)" --include="*.py" . | grep -v ".archive/" | grep -v "__pycache__"
```

---

## Triage Rules

| Pattern | Context | Risk | Action |
|---------|---------|------|--------|
| `except: pass` | Data processing | 🔴 | Add `log_error()` + re-raise |
| `except: pass` | Cleanup/finally | 🟢 | Ignore |
| `return 0` after except | Parse/convert | 🟡 | Log + return None |
| `sys.exit(0)` | Except block (cron) | 🔴 | Change to `exit(1)` |
| `sys.exit(0)` | CLI usage help | 🟢 | Ignore |
| False green | no_agent cron | 🔴 | Reinstall or delete cron |

---

## Common Bugs Found (real 2026-07-29 session)

### Missing function after copy-paste
- `col_telegram_intake.py:102` — `_token()` undefined (dropped when copying from `hourly_regen_commit_watcher.py`)
- `col_telegram_intake.py:46` — `import urllib.request` missing

### Subprocess argument truncation (Windows)
- `col_queue_handler.py:234` — `subprocess.run([..., long_text])` can truncate on Windows
- Fix: use `input=text` (stdin pipeline) instead of command-line argument

## Output Format

```
🔍 SILENT-FAILURE AUDIT — [date]
🔴 [N] CRITICAL · 🟡 [N] WARNING · 🟢 [N] OK
─── CRITICAL ──────────────────────────────
🔴 SWALLOWED ERROR: <file>:<line>
🔴 FALSE GREEN: <cron> — script missing
...
```

## Pitfalls

- **Archived scripts:** Exclude `.archive/` directory
- **Dotfolder:** `search_files` blind to `.scripts/` — use `terminal` + `grep`/`find`
- **Context matters:** Always check ±5 lines around each match before flagging
- **Not runtime:** This is static analysis only. Runtime bugs (API timeout, cold-path import) require execution testing.
