# No-Agent Wrapper Cron Pattern — reuse vault-SSOT orchestrator

Worked skeleton cho mô hình: no_agent cron wrapper bọc 1 orchestrator ĐÃ CÓ trong
`vault/.scripts/` (SSOT, verified) qua absolute subprocess path — KHÔNG copy orchestrator
vào `profile/scripts/` (tránh duplicate drift, M1). Build từ LTO cron 2026-07-28.

## Kiến trúc

```
cron resolver → profile/scripts/lto_weekly_cron.py (bare name, no_agent)
                    │
                    └─ subprocess.run([py, VAULT_ROOT/.scripts/weekly_lto_sql.py, --week, WID])
                            │  (absolute path — KHÔNG bị resolver chặn)
                            └─ orchestrator query SQL IKKO → ghi 04_LTO_Weekly_Log.md
                    └─ wrapper đọc log → format TG 🟢 / guard-skip / TG 🔴 on fail
```

## 1. Wrapper skeleton (GREEN — viết SAU khi test RED)

```python
#!/usr/bin/env python3
import io, os, re, sys, subprocess, urllib.error, urllib.parse, urllib.request
from datetime import date, timedelta
from pathlib import Path

try:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
except (ValueError, AttributeError):
    pass

SCRIPT_DIR = Path(__file__).resolve().parent
VAULT_ROOT = Path(r"C:\Users\khoans\Documents\Warren_OS_Local\vault")  # hardcode (CWD≠vault)
LOG_FILE = VAULT_ROOT / "10_OPERATION_DATA" / "04_LTO_Weekly_Log.md"
ORCHESTRATOR = VAULT_ROOT / ".scripts" / "weekly_lto_sql.py"
CHAT_ID = "2117653672"
ENV = Path(r"C:\Users\khoans\AppData\Local\LUsineWorkBot\.env")
MAX_RETRY = 3

def _monday_of_yesterday(ref: date = None) -> date:
    ref = ref or date.today()
    yesterday = ref - timedelta(days=1)
    return yesterday - timedelta(days=yesterday.weekday())  # ISO Monday tuần chứa yesterday

def compute_current_week_label(ref: date = None) -> str:
    mon = _monday_of_yesterday(ref)
    iso = mon.isocalendar()
    return "{}-W{:02d}".format(iso[0], iso[1])

def should_skip(log_text: str, week_id: str) -> bool:
    pat = r"^##\s+" + re.escape(week_id) + r"\s*\|.*?PROMO MEASUREMENT \(B\+C\)"
    return bool(re.search(pat, log_text, re.MULTILINE | re.DOTALL))

def _get_bot_token() -> str | None:
    if not ENV.exists():
        return None
    for ln in open(ENV, encoding="utf-8-sig"):
        m = re.search(r"TELEGRAM_BOT_TOKEN=(.+)", ln)
        if m:
            return m.group(1).strip()
    return None

def _send_telegram(text: str) -> bool:
    token = _get_bot_token()
    if not token:
        print("ERROR: TELEGRAM_BOT_TOKEN not found", file=sys.stderr)
        return False
    url = "https://api.telegram.org/bot{}/sendMessage".format(token)
    data = urllib.parse.urlencode({"chat_id": CHAT_ID, "text": text}).encode("utf-8")
    try:
        with urllib.request.urlopen(urllib.request.Request(url, data=data, method="POST"), timeout=10) as r:
            return r.status == 200
    except Exception as e:
        print("TG error: {}".format(e), file=sys.stderr)
        return False

def format_tg_summary(block: str, week_id: str) -> str:
    def _cov(title):
        m = re.search(r"### 📊 [BC]\. .*?" + re.escape(title) +
                      r".*?\| Covers khung giờ \| (\d+)", block, re.MULTILINE | re.DOTALL)
        return m.group(1) if m else "—"
    b = _cov("SUNSET HH — LU5"); c = _cov("MORNING KICKSTART — LU7")
    head = re.search(r"^##\s+(\S+)\s*\|", block, re.MULTILINE)
    lbl = head.group(1) if head else week_id
    return "🟢 LTO Weekly — {}\nB (Sunset LU5): covers {}\nC (Kickstart LU7): covers {}".format(lbl, b, c)

def run_orchestrator(week_id: str, dry: bool = False) -> str:
    cmd = [sys.executable, str(ORCHESTRATOR), "--week", week_id]
    if dry:
        cmd.append("--dry")
    last_err = ""
    for attempt in range(1, MAX_RETRY + 1):
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", timeout=60)
            if r.returncode == 0:
                return r.stdout
            last_err = r.stderr[-800:]
        except Exception as e:
            last_err = str(e)
        print("[retry {}/{}] {}".format(attempt, MAX_RETRY, last_err), file=sys.stderr)
    raise RuntimeError("orchestrator failed after {} retries: {}".format(MAX_RETRY, last_err))

def main() -> int:
    week_id = compute_current_week_label()
    print("[cron] week_id = {}".format(week_id))
    log_text = LOG_FILE.read_text(encoding="utf-8") if LOG_FILE.exists() else ""
    if should_skip(log_text, week_id):
        _send_telegram("ℹ️ LTO Weekly {} đã có log — skip (no spam)".format(week_id))
        return 0
    try:
        run_orchestrator(week_id, dry=False)
    except Exception as e:
        _send_telegram("🔴 LTO Weekly cron FAIL:\n{}".format(str(e)[:800]))
        return 1
    new_text = LOG_FILE.read_text(encoding="utf-8")
    m = re.search(r"^##\s+" + re.escape(week_id) + r"\s*\|.*?PROMO MEASUREMENT \(B\+C\).*?(?=^##\s|\Z)",
                  new_text, re.MULTILINE | re.DOTALL)
    block = m.group(0) if m else new_text
    _send_telegram(format_tg_summary(block, week_id))
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

## 2. RED test (viết TRƯỚC — import wrapper → fail vì chưa có file)

```python
# tests/test_lto_weekly_cron.py
import importlib, sys, unittest
from datetime import date
from pathlib import Path
from unittest import mock
SCRIPT_DIR = Path(__file__).resolve().parent.parent  # profile/scripts
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

def load_wrapper():
    return importlib.import_module("lto_weekly_cron")  # ModuleNotFoundError -> RED

class TestWeekLabel(unittest.TestCase):
    def test_monday_returns_prev_week(self):
        m = load_wrapper()
        # Cron chạy T2 27/07/2026 -> yesterday=CN 26/07 -> tuần đóng sổ = 2026-W30
        self.assertEqual(m.compute_current_week_label(date(2026,7,27)), "2026-W30")

class TestGuardSkip(unittest.TestCase):
    def test_skip_when_week_present(self):
        m = load_wrapper()
        self.assertTrue(m.should_skip("## 2026-W30 | x — PROMO MEASUREMENT (B+C)\n", "2026-W30"))
    def test_no_false_positive_on_W300(self):
        m = load_wrapper()
        self.assertFalse(m.should_skip("## 2026-W300 | x — PROMO MEASUREMENT (B+C)\n", "2026-W30"))

class TestMainFlow(unittest.TestCase):
    def _setup(self):
        m = load_wrapper()
        self.tmp = Path(m.__file__).parent / "_test_lto_log_tmp.md"
        m.LOG_FILE = self.tmp
        return m
    def tearDown(self):
        if self.tmp.exists(): self.tmp.unlink()
    def test_main_skip_path(self):
        m = self._setup(); self.tmp.write_text("## 2026-W30 | x — PROMO MEASUREMENT (B+C)\n", encoding="utf-8")
        with mock.patch.object(m,"compute_current_week_label",return_value="2026-W30"), \
             mock.patch.object(m,"_send_telegram",return_value=True) as tg:
            self.assertEqual(m.main(), 0)
            self.assertIn("skip", tg.call_args[0][0].lower())
    def test_main_runs_and_reports_green(self):
        m = self._setup(); self.tmp.write_text("", encoding="utf-8")
        fake = "## 2026-W30 | x — PROMO MEASUREMENT (B+C)\n### 📊 B. SUNSET HH — LU5 (18:00–21:00)\n| Covers khung giờ | 82 | 90.2 | -9.1% | FAIL |\n### 📊 C. MORNING KICKSTART — LU7 (10:00–12:00)\n| Covers khung giờ | 160 | 168.0 | -4.8% | FAIL |\n"
        with mock.patch.object(m,"compute_current_week_label",return_value="2026-W30"), \
             mock.patch.object(m,"run_orchestrator",return_value=fake), \
             mock.patch.object(m,"_send_telegram",return_value=True) as tg:
            self.assertEqual(m.main(), 0)
            self.assertIn("🟢", tg.call_args[0][0])
    def test_main_fails_red(self):
        m = self._setup(); self.tmp.write_text("", encoding="utf-8")
        with mock.patch.object(m,"compute_current_week_label",return_value="2026-W30"), \
             mock.patch.object(m,"run_orchestrator",side_effect=RuntimeError("VPN down")), \
             mock.patch.object(m,"_send_telegram",return_value=True) as tg:
            self.assertEqual(m.main(), 1)
            self.assertIn("🔴", tg.call_args[0][0])

if __name__ == "__main__":
    unittest.main(verbosity=2)
```

Chạy: `cd profile/scripts && python tests/test_lto_weekly_cron.py` (pytest thường chưa cài → dùng unittest native).
RED = ModuleNotFoundError. GREEN = 11/11 OK.

## 3. Gotchas đã bắt (LTO build)
- Test assertion sai format → sửa assertion, KHÔNG sửa code để pass (giữ TDD nghiêm).
- `compute_current_week_label` dùng `isocalendar()[1]` của yesterday rồi cộng tuần → lệch 1 tuần.
  FIX: `_monday_of_yesterday = yesterday - timedelta(days=yesterday.weekday())` (robust qua năm).
- Cron resolver CHỈ gọi bare name `profile/scripts/lto_weekly_cron.py`. Orchestrator gọi qua
  subprocess absolute path → không bị chặn. Copy orchestrator vào profile/scripts là THỪA.
- 9-điểm (§15) embed: fail🔴 / ok🟢 / guard-skip / no_agent / không tự commit.
