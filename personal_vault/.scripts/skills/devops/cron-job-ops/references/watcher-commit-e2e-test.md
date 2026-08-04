# Watcher Commit E2E Test Pattern (RED-GREEN + rollback)

Skill: `cron-job-ops` §12.5 / §12.6. Recipe test 1 no_agent Telegram watcher bắt
approval → git commit/push, rollback sạch, KHÔNG làm hỏng repo thật. Dùng cho
`hourly_regen_commit_watcher.py` (trigger "ok 09", commit 2 file) 2026-07-27.

## 1. Unit test (RED-GREEN) — filter + files

```python
# _test_watcher.py
import sys, importlib.util
from pathlib import Path
SCRIPT = Path(r"vault/.scripts/hourly_regen_commit_watcher.py")
spec = importlib.util.spec_from_file_location("watcher", str(SCRIPT))
W = importlib.util.module_from_spec(spec); spec.loader.exec_module(W)

def test_trigger_exact():
    assert W.is_commit_trigger("ok 09") and W.is_commit_trigger("OK 09")
    assert W.is_commit_trigger("ok  09")  # extra space normalized

def test_trigger_negative():
    # unique per cron - must NOT clash with col ('ok') / review / old 'ok hourly'
    for bad in ["ok", "ok push", "ok hourly", "09 ok", "ok 09x", "oke", ""]:
        assert not W.is_commit_trigger(bad)

def test_files():
    f = W.commit_target_files()
    assert len(f) == 2 and "09_Hourly_Cover_Revenue_Log.md" in f[0]

if __name__ == "__main__":
    try:
        test_trigger_exact(); test_trigger_negative(); test_files()
        print("[ALL GREEN]"); sys.exit(0)
    except Exception as ex:
        print(f"[RED] {ex}"); sys.exit(1)
```

Run: `cd Warren_OS_Local && python3 vault/.scripts/_test_watcher.py`

## 2. Guard test (skip when week committed)

```python
# _test_watcher_guard.py — patch STATE/OFFSET/ENV to tmp, no real TG
def test_guard_skips_when_week_committed(tmp_path):
    state = tmp_path / ".state.json"
    week = W.current_week_label()
    state.write_text(json.dumps({"last_committed_week": week}))
    W.STATE_FILE = state; W.OFFSET_FILE = tmp_path/".off.json"
    W.ENV_FILE = tmp_path/".env"
    W.ENV_FILE.write_text("TELEGRAM_BOT_TOKEN=x\nTELEGRAM_ALLOWED_USERS=1\n")
    import io, contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        W.main()
    assert "[SKIP]" in buf.getvalue()
```

## 3. E2E commit+rollback (isolate state, temp file, reset --hard)

```python
# _e2e_watcher_final.py
def main():
    W.STATE_FILE = Path(TMP)/".state.json"; W.OFFSET_FILE = Path(TMP)/".off.json"
    W.ENV_FILE = Path(TMP)/".env"; W.ENV_FILE.write_text("TELEGRAM_BOT_TOKEN=x\nTELEGRAM_ALLOWED_USERS=1\n")
    before = run_git(["rev-parse","HEAD"])
    testf = REPO/"_e2e_watch_tmp.txt"; testf.write_text("x\n")
    W.COMMIT_FILES = ["_e2e_watch_tmp.txt"]
    short = W.do_commit_push()           # includes pull --rebase + push
    assert short
    W._save_state(W.current_week_label())
    # re-run main() -> SKIP (no 409, no double commit)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf): W.main()
    assert "[SKIP]" in buf.getvalue()
    run_git(["reset","--hard",before])   # rollback
    if testf.exists(): testf.unlink()
```

**Verify:** `git status` sau rollback = CLEAN (chỉ hiện file test tạm GG tạo riêng).
Push thật lên remote confirm được (hash xuất hiện trên `origin/master`), rồi
`reset --hard` về `before` → remote KHÔNG bị ảnh hưởng (remote đã có commit,
local chỉ lùi con trỏ). Đây là an toàn: remote giữ commit test, local sạch.
Nếu muốn remote cũng sạch → `git push origin --delete <test_hash>` (tránh force-push
trên branch chung).

## 4. Pitfalls bắt thực tế (2026-07-27)
- **P1 non-fast-forward:** `do_commit_push` PHẢI `git pull --rebase origin HEAD`
  trước `git push` (Bố push từ máy khác → reject non-fast-forward).
- **P2 import heavy module fail:** watcher KHÔNG import regen script (parser cần
  VPN/sqlclient → exec dừng giữa chừng → `module has no attribute`). Tính week
  label bằng hàm local 5 dòng (compute_current_week_label).
- **P3 409 conflict:** main bot `LUsineWorkBot` chiếm getUpdates connection → watcher
  poll lần nào cũng 409. Fix: week-guard (chỉ poll khi tuần CHƯA commit) + private
  offset file. Production: dedicated bot token riêng (cron-job-ops §12 Option 1).
- **Mojibake:** no_agent script print ASCII; TG message dùng `send_telegram_plain`
  (no parse_mode) vì vault filenames có `_` → Markdown 400 (telegram-py-checklist Pitfall 2).
- **Warren 7-point cron comms:** fail→🔴+báo, success→✅+phân tích, unique trigger
  "ok 09", ack receipt ngay ("nhận được"), fallback GC recurring. Xem §12.6 + WARREN_MEMORY.

## 5. Cron architecture (LLM + no_agent watcher)
- Cron A (agent, T2 7g, deepseek-v4-flash): regen → fail🔴 / OK → phân tích sâu → TG deliver=all → "Reply OK 09 để push".
- Cron B (no_agent, */30 7-17 * * 1): poll TG "ok 09" → commit 2 file → TG "✅ Da push <hash>".
- NEVER tự commit nếu chưa có "ok 09" từ Bố.
