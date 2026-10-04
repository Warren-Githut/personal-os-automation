# No-Agent Parser Cron Pattern (item-sales-weekly, 2026-07-27)

Working skeleton + post-mortem cho mọi cron `no_agent` chạy parser → ghi vault + dashboard + verify + Telegram (KHÔNG tự push, rule 15).

## Architecture đúng

```
cron T2 09:00 → item_sales_cron_runner.main()
  1. compute_run_week()      # calendar year, khớp make_week_id
  2. should_run() guard      # skip nếu log đã có tuần (chống dup/spam)
  3. _run_parser()            # subprocess: item_sales_sql_parser.py --live --emit-html <TEMPLATE>
                               #   parser ghi TRACKER (newest-on-top) + BUILT_HTML (không đụng template)
  4. verify_item_sales_cron.verify(LOG_FILE, week_id, BUILT_HTML)
                               #   assert: 1 block ## Wxx + HTML </script> đóng + KHÔNG __PAYLOADS__ leftover
                               #   FAIL → exit(2), KHÔNG ghi thêm, KHÔNG push
  5. OK → Telegram XANH + "🔔 gõ 'ok 11' để GG commit+push"
```

## Runner skeleton (copy-paste base)

```python
import os, sys, re, subprocess
from datetime import date, timedelta
from pathlib import Path

# VAULT_ROOT: override qua env var nếu vault ở chỗ khác
VAULT_ROOT = Path(os.environ.get("VAULT_ROOT", r"C:/Users/khoans/Documents/Warren_OS_Local/vault"))
HERE = Path(__file__).resolve().parent          # .resolve() BẮT BUỘC
sys.path.insert(0, str(HERE))
LOG_FILE = VAULT_ROOT / "10_OPERATION_DATA" / "<tracker>.md"
TEMPLATE = VAULT_ROOT / "30_KNOWLEDGE_BASE" / "wiki" / "dashboards" / "<x>.template.html"  # INPUT, read-only
PARSER = HERE / "<parser>.py"
BUILT_HTML = VAULT_ROOT / "30_KNOWLEDGE_BASE" / "wiki" / "dashboards" / "<x>.html"          # OUTPUT, verify inspect
PROFILE_SCRIPTS = Path(r"C:/Users/khoans/AppData/Local/hermes/profiles/warren-profile/scripts")
sys.path.insert(0, str(PROFILE_SCRIPTS))
try:
    from _send_telegram import send_telegram
except Exception:
    send_telegram = None

def compute_run_week(ref=None):
    """Calendar year (khớp make_week_id), KHÔNG iso year."""
    if ref is None: ref = date.today()
    monday = ref - timedelta(days=ref.weekday())
    prev = monday - timedelta(days=7)
    return f"{prev.year}-W{prev.isocalendar()[1]:02d}"

def should_run(week_id):
    if not LOG_FILE.exists(): return True
    txt = LOG_FILE.read_text("utf-8")
    # regex anchor `|` để W30 không match W30x (template header format ## YYYY-Www | ...)
    return len(re.findall(rf"^##\s+{re.escape(week_id)}\s*\|", txt, re.MULTILINE)) == 0

def _run_parser(week_id):
    try:
        r = subprocess.run([sys.executable, str(PARSER), "--live", "--emit-html", str(TEMPLATE)],
                           capture_output=True, text=True, encoding="utf-8", cwd=str(HERE))
        if r.returncode != 0:
            print(r.stderr, file=sys.stderr); return False
        return True
    except Exception as e:
        print(f"[ERR] parser: {e}", file=sys.stderr); return False

def main(week_override=None):
    week_id = week_override or compute_run_week()
    print(f"[RUN] {week_id}")
    if not should_run(week_id):
        print(f"[SKIP] {week_id} đã có — không chạy lại"); return 0
    if not _run_parser(week_id):
        _send_tg(f"🔴 [FAIL] item-sales {week_id} — parser lỗi (SQL/VPN?)."); return 2
    from verify_item_sales_cron import verify
    fails = verify(LOG_FILE, week_id, BUILT_HTML)
    if fails:
        _send_tg("🔴 [FAIL] item-sales " + week_id + " — " + "\n".join(fails)); return 2
    _send_tg(f"🟢 [OK] item-sales {week_id} — regen xong.\n🔔 Gõ 'ok 11' để GG commit+push.")
    return 0
```

## Verify gate (structural, KHÔNG circular)

```python
def verify(tracker, week_id, html):
    fails = []
    txt = tracker.read_text("utf-8") if tracker.exists() else ""
    cnt = len(re.findall(rf"^##\s+{re.escape(week_id)}\s*\|", txt, re.MULTILINE))
    if cnt == 0: fails.append(f"tracker: thiếu block {week_id}")
    elif cnt > 1: fails.append(f"tracker: block {week_id} trùng {cnt} lần")
    h = html.read_text("utf-8") if html.exists() else ""
    if "<script" in h and "</script>" not in h:
        fails.append("html: thiếu </script> đóng (chart trắng)")
    if "__PAYLOADS__" in h:
        fails.append("html: còn __PAYLOADS__ chưa thay (stale)")
    return fails
```

## Bug post-mortem (4 bugs, reviewer-node bắt)

| # | Bug | Symptom | Fix |
|---|-----|---------|-----|
| 1 | Year mismatch | runner ISO year vs parser calendar year → ~1 tuần/năm verify sai tuần | dùng `prev.year` không `isocalendar()[0]` |
| 2 | Verify wrong file | parser ghi template, runner verify built → gate dead (luôn pass) | parser ghi built, runner verify built |
| 3 | Template clobber | parser ghi đè template → tuần 2 `__PAYLOADS__` mất → silent no-op | parser `out = tpl.with_name(tpl.name.replace(".template.html",".html"))` |
| 4 | `HERE` no `.resolve()` | cwd ≠ script dir → subprocess resolve sai | `HERE = Path(__file__).resolve().parent` |

**Critic false-claim:** reviewer-node báo "không có file item_sales_trend*.html" nhưng `ls` confirm CẢ 2 tồn tại. → verify disk trước khi tin critic.

## TDD gate cho build

- `test_verify_*.py`: 5 cases (pass / dup / no-`</script>` / `__PAYLOADS__` leftover / week absent) → RED→GREEN.
- `test_runner_*.py`: compute_run_week (assert W30 cho 2026-07-27, KHÔNG W29), should_run guard (skip nếu có), main flow (skip/parser-fail/verify-fail/ok).
- `test_year_boundary.py`: loop 52 Mondays + ISO-vs-calendar edge (2024-12-30 → 2024-W01).

## Post-edit sync (§1.5)

Sau mọi edit `vault/.scripts/` → copy + md5 vào `profile/scripts/` + copy submodule (`sqlserver_client/`) nếu import. Test: `python3 -m pytest tests/ -q`.
