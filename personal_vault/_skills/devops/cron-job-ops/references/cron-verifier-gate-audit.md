# Cron Verifier-Gate Audit — Recipe + Bug Transcripts

> Companion to `cron-job-ops` §11.8. (Note: `audit-automation` is curator-blocked for autonomous patch — verifier-gate technique lives here instead.)
> Mục đích: phát hiện crons **nuốt lỗi → báo sai/silent** (theo @vartekxx "verifier gate = reject bad work, KHÔNG silent").

## Grep recipe (chạy trên disk, KHÔNG search_files)

```bash
# no_agent script: tìm verifier cứng
grep -inE "verify|assert|raise|exit\(" vault/.scripts/<name>.py
#   ✅ có sys.exit(1) / raise trên branch lỗi = verifier cứng
#   ❌ CHỈ except: pass / return [] / return None = silent-failure gap

# LLM cron: đọc prompt field trong cronjob list — có bước check không?
```

## 2 real bugs (2026-07-25, warren-profile)

### Bug 1 — quota.py (job d235537ac561, Model Router Daily Report)
- **Symptom:** daily report in "0% Pro" sai sự thật khi `quota_state.json` corrupt.
- **Root cause:** `load_state()` `except (json.JSONDecodeError, OSError):` → auto-reset `DEFAULT_STATE` + `save_state` + `return state` (exit 0). Swallow + silent reset.
- **Fix:**
  ```python
  except (json.JSONDecodeError, OSError) as e:
      print(f"[quota] ERROR: quota_state.json corrupted/unreadable: {e}", file=sys.stderr)
      print("[quota] Refusing to auto-reset — manual fix needed", file=sys.stderr)
      sys.exit(1)
  ```
- **Verify:** `echo "{ bad" > quota_state.json && python3 quota.py report; echo $?` → `exit 1` ✅; normal → `exit 0` ✅.

### Bug 2 — col_telegram_intake.py (job 16d81e801a39)
- **Symptom:** intake chết câm vĩnh viễn khi Telegram token hết hạn / mạng chết (không alert).
- **Root cause:** `_get_updates()` `except: return []` → `main()` `if not updates: return` (silent no-op). Fail = empty list = no-op.
- **Fix:**
  ```python
  # _get_updates:
  except Exception as e:
      print(f"[intake] getUpdates error: {e}", file=sys.stderr)
      return None   # fail sentinel, KHÔNG []
  # main():
  updates = _get_updates(token, offset)
  if updates is None:
      print("[intake] FATAL: Telegram getUpdates failed — check token/network", file=sys.stderr)
      sys.exit(1)
  if not updates:
      return  # silent no-op CHỈ khi thật sự rỗng
  ```
- **Verify:** `python3 -m py_compile col_telegram_intake.py` OK (live chưa test — cần token).

## Pitfalls (reviewer-node A10 bắt 2026-07-25)
- ĐỪNG credit verifier sai layer — verify nằm ở pipeline downstream (vd revweek 3-layer ở `run_weekly_revenue_pipeline`, không ở intake poller). Ghi rõ "verify tại pipeline, chưa spot-check script".
- ĐỪNG claim "gap duy nhất" khi chưa đọc hết script — luôn `read_file` trực tiếp mọi script nghi vấn.
