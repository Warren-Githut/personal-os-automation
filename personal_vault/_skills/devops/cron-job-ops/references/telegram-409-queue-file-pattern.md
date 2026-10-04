# Telegram 409 — Queue-File Pattern (Option D, RECOMMENDED)

## When to use
Building a `no_agent` watcher that needs Warren's approval/trigger from Telegram,
but the main bot `LUsineWorkBot/launch_bot.py` already holds the long-poll
connection (aiogram, 24/7). Any second `getUpdates` caller → HTTP 409 Conflict.

Warren does NOT want a new bot, does NOT want to kill the main bot. → Solve 409
WITHOUT touching the Telegram connection: the main bot WRITES A FILE, the
watcher READS THE FILE.

## Architecture
```
Warren types "ok 09" in LUsineWorkBot
        │
        ▼
main bot handle_text()  ──►  _append_hourly_approval()
        │                       json.dump append to
        │                       .hourly_approval_queue.json
        │                       (NO getUpdates, keeps connection)
        ▼
hourly-regen-commit-watcher (no_agent, */30 7-17 * * 1)
        │
        ├─ reads .hourly_approval_queue.json
        ├─ if "ok 09" present → commit + push 2 files
        ├─ sends TG OUTBOUND (red/green) via send_telegram_plain()
        └─ writes "[]" to consume queue
```

## Bot side (telegram_bot.py)
Add near top of `handle_text()`, BEFORE all other handlers:

```python
# queue file lives in vault/.scripts/ (dotfolder, gitignored-safe)
_HOURLY_QUEUE = VAULT_SCRIPTS / ".scripts" / ".hourly_approval_queue.json"
import json as _json, re as _re

def _append_hourly_approval(user_id: int, text: str) -> bool:
    if not text:
        return False
    clean = _re.sub(r"\s+", " ", text.strip().lower())
    if clean != "ok 09":          # unique trigger, avoids clashing col/review
        return False
    entry = {"user_id": user_id, "text": text.strip(), "ts": _dt_iso_now()}
    try:
        q = []
        if _HOURLY_QUEUE.exists():
            try:
                q = _json.loads(_HOURLY_QUEUE.read_text(encoding="utf-8"))
            except Exception:
                q = []
        q.append(entry)
        _HOURLY_QUEUE.write_text(_json.dumps(q, ensure_ascii=False, indent=2), encoding="utf-8")
        return True
    except Exception as e:
        log.exception(f"[hourly] queue write failed: {e}")
        return False

# in handle_text():
if _append_hourly_approval(message.from_user.id, text):
    await message.answer("✅ Nhận được 'OK 09' — đã ghi queue. Watcher sẽ commit+push 2 file hourly.")
    return
```

## Watcher side (no_agent script)
```python
QUEUE_FILE = VAULT_ROOT / ".scripts" / ".hourly_approval_queue.json"

def main():
    queue = json.loads(QUEUE_FILE.read_text()) if QUEUE_FILE.exists() else []
    pending = [e for e in queue if is_commit_trigger(e.get("text", ""))]
    if not pending:
        return                       # no-op, no 409 (never polls TG)
    # ... commit + push 2 scoped files ...
    QUEUE_FILE.write_text("[]", encoding="utf-8")   # consume
```

## Why this beats dedicated bot (Option 1)
- No new token, no BotFather, no change to Warren's habit (types in same bot).
- Zero 409 by construction (watcher never calls getUpdates).
- Bot only writes; watcher only reads → clean separation, easy debug.

## Pair with git-corruption rule (see §11.10 / §12.6 P1)
Watcher MUST NOT `git pull --rebase` / `git reset --hard` / `git stash`.
On push reject → red TG + sys.exit(1), Bố resolves manually.

## Real deployment (2026-07-27)
- Cron A `hourly-regen-deepanalysis` (T2 7:00, LLM deepseek-v4-flash chính hãng)
  regen + gửi báo cáo phân tích sâu.
- Warren replies "ok 09" → bot writes queue → Cron B
  `hourly-regen-commit-watcher` (T2 7-17g/30p, no_agent) reads → commits
  09_Hourly_Cover_Revenue_Log.md + dashboard → green TG "Da push <hash>".
- E2E verified: queue→commit→push→consume, rollback clean, repo NOT corrupted.
