# No-Agent Vault-Scan Script Skeleton (copy-paste base)

Dùng cho mọi Hermes `no_agent:true` cron quét vault (orphan / SSOT-conflict / gap /
lint). 0 token, stdlib only, Telegram best-effort, `--dry-run` safe.

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""<name>_cron.py -- nightly vault scanner (no_agent, 0 token)."""
import os, re, sys, json
from datetime import datetime, date
from pathlib import Path

VAULT_ROOT = Path(os.environ.get(
    "VAULT_ROOT", r"C:/Users/khoans/Documents/Warren_OS_Local/vault"))
PROFILE_SCRIPTS = Path(__file__).resolve().parent
LOG_FILE = VAULT_ROOT / "00_CORE_LOGIC" / "<NAME>_LOG.md"
STATE_FILE = VAULT_ROOT / ".scripts" / ".<name>_state.json"

sys.path.insert(0, str(PROFILE_SCRIPTS))
try:
    from _send_telegram import send_telegram
except Exception:
    def send_telegram(text):
        return {"ok": False, "error": "import_failed"}

EXCLUDE_DIRS = {".scripts", ".archives", "_archives", ".git", "node_modules",
                "__pycache__", ".accumulation", "_assets", "vendor"}
EXCLUDE_SUFFIX = (".pyc",)

class Findings:
    def __init__(self): self.items = []
    def add(self, level, kind, msg):
        self.items.append({"level": level, "kind": kind, "msg": msg})
    def has(self): return len(self.items) > 0

def load_state():
    try:
        if STATE_FILE.exists():
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except Exception: pass
    return {"last_run": None, "resolved_ids": []}

def save_state(s):
    try:
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        STATE_FILE.write_text(json.dumps(s, ensure_ascii=False), encoding="utf-8")
    except Exception as e:
        print(f"[WARN] state save failed: {e}")

def scan(f: Findings):
    # B2 orphan example (user-facing only):
    for p in VAULT_ROOT.rglob("*"):
        if not p.is_file(): continue
        rel = p.relative_to(VAULT_ROOT)
        if rel.parts and rel.parts[0].startswith("."): continue
        if any(part in EXCLUDE_DIRS for part in rel.parts): continue
        if p.suffix.lower() in EXCLUDE_SUFFIX: continue
        if p.stat().st_size == 0:
            f.add("yellow", "orphan", f"File 0-byte: {rel}")
    # B1 conflict / B3 gap: add your parsers here (strict regex, None if rụng)

def write_log(f, state):
    if not f.has(): return
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    block = [f"## 🔎 <Name> Scan — {stamp}", ""]
    c = {"red":0,"yellow":0,"green":0}
    for it in f.items:
        icon = {"red":"🔴","yellow":"🟡","green":"🟢"}[it["level"]]
        c[it["level"]] += 1
        block.append(f"- [{icon} **{it['kind']}**] {it['msg']} — status: open")
    block += ["", f"_Summary: 🔴{c['red']} 🟡{c['yellow']} 🟢{c['green']}_", "", "---", ""]
    old = LOG_FILE.read_text(encoding="utf-8") if LOG_FILE.exists() else ""
    LOG_FILE.write_text("\n".join(block) + old, encoding="utf-8")
    state["last_run"] = stamp; save_state(state)

def main():
    dry = "--dry-run" in sys.argv
    f = Findings(); scan(f); state = load_state()
    if not f.has():
        print("OK: no issues found. Silent."); return
    write_log(f, state)
    lines = ["🔎 *<Name> — " + date.today().isoformat() + "*"] + [
        f"{'🔴🟡🟢'[i]} {it['kind']}: {it['msg']}" for i,it in enumerate(f.items)]
    tg = "\n".join(lines)
    if dry:
        print("=== DRY-RUN (no Telegram) ===\n" + tg)
    else:
        res = send_telegram(tg)
        print(f"TG_RESULT:{'OK' if res.get('ok') else 'FAIL'}|{str(res.get('error',''))[:80]}")

if __name__ == "__main__":
    main()
```

## Verify gate (trước báo Bố xong)
1. `python3 -m py_compile <name>_cron.py` → COMPILE OK
2. `python3 <name>_cron.py --dry-run` → in kết quả, KHÔNG gửi TG
3. Inject 1 finding giả (vd tạo file 0-byte trong `10_OPERATION_DATA/`) → assert bắt được → revert
4. `cronjob(action='run')` → `execution_success: true`
5. `git add -f cron/jobs.json scripts/<name>_cron.py` + commit + push
