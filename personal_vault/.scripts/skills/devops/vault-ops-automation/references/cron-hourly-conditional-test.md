# cron-hourly-conditional-test.md

Reusable recipe for unit-testing a no_agent cron script whose behaviour
branches on the current hour (e.g. `gen_today_and_send.py` Option C:
hourly gen, 10:00 Telegram brief, any gen failure → alert).

## The trap

The script imports `from datetime import datetime`, so `datetime` is an
attribute of the **module namespace** (`gts.datetime`), NOT a submodule
path `gen_today_and_send.datetime`. Patching
`mock.patch("gen_today_and_send.datetime")` creates a NEW attribute and
**silently no-ops** — the real `datetime.now().hour` still runs, so the
test exercises the wrong branch and the assertions mislead you.

## Correct patch target

`mock.patch.object(gts, "datetime", create=True, **{"now.return_value": fake_now})`
where `gts` is the loaded module and `fake_now` is a MagicMock carrying `.hour`.

## Full recipe (ad-hoc, no real Telegram sent)

```python
import sys, importlib.util
from pathlib import Path
from unittest import mock

SCRIPTS = Path(r"C:\Users\khoans\Documents\Warren_OS_Local\vault\scripts")
sys.path.insert(0, str(SCRIPTS))
spec = importlib.util.spec_from_file_location("gts", SCRIPTS/"gen_today_and_send.py")
gts = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gts)

calls = {"gen": 0, "brief": 0}
def fake_run(name, timeout=90):
    calls["gen" if name == "gen_today.py" else "brief"] += 1
    return (True, "ok")

def set_hour(h):
    fake_now = mock.MagicMock(); fake_now.hour = h
    return mock.patch.object(gts, "datetime", create=True, **{"now.return_value": fake_now})

with mock.patch.object(gts, "run", side_effect=fake_run), \
     mock.patch.object(gts, "send_telegram", return_value={"ok": True}) as st:
    gts._heartbeat = mock.MagicMock()   # real one is imported INSIDE main()

    # Case 1: non-10 -> silent
    calls.clear(); calls.update(gen=0, brief=0)
    with set_hour(14):
        try: gts.main()
        except SystemExit as e: rc = e.code
    assert rc == 0 and calls["gen"]==1 and calls["brief"]==0 and st.call_count==0

    # Case 2: 10:00 -> brief
    calls.clear(); calls.update(gen=0, brief=0)
    with set_hour(10):
        try: gts.main()
        except SystemExit as e: rc = e.code
    assert rc == 0 and calls["gen"]==1 and calls["brief"]==1 and st.call_count==0

    # Case 3: gen FAIL -> alert
    calls.clear(); calls.update(gen=0, brief=0)
    def fail(name, timeout=90):
        calls["gen" if name=="gen_today.py" else "brief"] += 1
        return (False,"boom") if name=="gen_today.py" else (True,"ok")
    with mock.patch.object(gts,"run",side_effect=fail), set_hour(10):
        try: gts.main()
        except SystemExit as e: rc = e.code
    assert rc==1 and st.call_count==1
```

Notes:
- `_heartbeat` is imported inside `main()`, so inject `gts._heartbeat = mock.MagicMock()`
  AFTER `exec_module` and BEFORE calling `main()` (no need to patch import machinery).
- Run the ad-hoc file under `C:\Users\khoans\AppData\Local\Temp\hermes-verify-<name>.py`,
  then `rm` it. The `ls` at the end returns exit 2 (file gone) — that is the
  desired cleanup signal, NOT a test failure.
- Combine with the HOME-unset repro (`env -u HOME python3 ...`) when the script
  also touches GSheet/token paths.
