# WinError 64 — Transient Network Error in aiogram Polling (Windows)

## Symptom

```
08:13:00 | ERROR    | Failed to fetch updates - TelegramNetworkError: HTTP Client says - ClientOSError: [WinError 64] The specified network name is no longer available
08:13:00 | WARNING  | Sleep for 1.000000 seconds and try again... (tryings = 0, bot id = 8394552936)
08:13:11 | INFO     | Connection established (tryings = 1, bot id = 8394552936)
```

Bot recovers in ~11 seconds without human intervention.

## Root Cause

| Layer | Detail |
|-------|--------|
| **OS error** | `WinError 64` = `ERROR_NETNAME_DELETED` — Windows indicates the remote TCP connection was forcibly closed |
| **HTTP layer** | aiohttp (aiogram's HTTP client) raises `ClientOSError` when the TCP socket to Telegram's API server drops |
| **Bot layer** | aiogram's built-in polling loop catches `TelegramNetworkError`, logs ERROR, sleeps 1s (with exponential backoff), retries, and reconnects |

**This is NOT a code bug.** It is a transient Windows network stack event.

## Common Triggers on Windows

1. **Network fluctuation** — WiFi/ethernet briefly drops/reconnects
2. **Machine idle/sleep** — TCP connection times out while machine was asleep
3. **Firewall/AV interference** — Security software temporarily interrupts the connection
4. **VPN/proxy changes** — Routing table modification drops existing connections
5. **ISP routing** — Telegram server momentarily unreachable

## Why aiogram Catches It

aiogram 3.x uses long-polling: it opens an HTTP connection to Telegram's `getUpdates` endpoint and holds it open (long timeout). When the TCP connection drops, aiohttp raises `ClientOSError`. aiogram wraps this in `TelegramNetworkError`, logs it, and retries. **The retry usually succeeds immediately** because it opens a fresh TCP connection.

**In most cases, aiogram does NOT crash or exit** — the polling loop stays alive. The ERROR log is just noise.

## Fix: TransientNetworkFilter

Add a logging filter to downgrade WinError 64 ERROR/CRITICAL → WARNING:

```python
class TransientNetworkFilter(logging.Filter):
    """Downgrade transient Windows network errors from ERROR to WARNING.

    WinError 64 (ERROR_NETNAME_DELETED) is a transient TCP drop that
    aiogram's built-in retry handles automatically. Logging it as ERROR
    creates noise — downgrade to WARNING since it self-heals.
    """
    def filter(self, record: logging.LogRecord) -> bool:
        if "WinError 64" in record.getMessage() and record.levelno >= logging.ERROR:
            record.levelno = logging.WARNING
            record.levelname = "WARNING"
        return True


# Apply to aiogram logger — add after logging.basicConfig()
logging.getLogger("aiogram").addFilter(TransientNetworkFilter())
```

## Verification Script

```python
# Ad-hoc verification: run with Python 3.12
import logging

class TransientNetworkFilter(logging.Filter):
    def filter(self, record):
        if "WinError 64" in record.getMessage() and record.levelno >= logging.ERROR:
            record.levelno = logging.WARNING
            record.levelname = "WARNING"
        return True

f = TransientNetworkFilter()

# Test 1: WinError 64 ERROR -> WARNING
r = logging.LogRecord("aiogram", logging.ERROR, "", 0,
    "Failed to fetch updates - ...ClientOSError: [WinError 64] The specified network name is no longer available", (), None)
assert f.filter(r); assert r.levelno == logging.WARNING

# Test 2: Non-WinError ERROR stays ERROR
r = logging.LogRecord("aiogram", logging.ERROR, "", 0,
    "Failed to fetch updates - TelegramConflictError: ...", (), None)
assert f.filter(r); assert r.levelno == logging.ERROR

# Test 3: WARNING/INFO unchanged
r = logging.LogRecord("aiogram", logging.WARNING, "", 0, "Sleep for 1s...", (), None)
assert f.filter(r); assert r.levelno == logging.WARNING

r = logging.LogRecord("aiogram", logging.INFO, "", 0, "Connection established", (), None)
assert f.filter(r); assert r.levelno == logging.INFO

print("All tests passed. Filter works correctly.")
```

## Recovery Expectation

- **Typical recovery:** 1-15 seconds (1 retry cycle)
- **Worst case:** 30-60 seconds (3-4 retry cycles with backoff)
- **If recovery fails repeatedly (>1 minute):** Network issue is persistent, not transient. Check firewall, VPN, internet connectivity.

## When NOT to apply this filter

- Error is NOT `WinError 64` but another network error
- Error persists across multiple retry cycles (>30 seconds of continuous failure)
- Bot crashes/exits instead of retrying (the filter only supresses log noise — it does not change retry behavior)

---

## ⚠️ Real-World Finding: Bot Process CAN Die

While the error is typically transient and aiogram's retry mechanism works, **the bot process can still exit** after a WinError 64 event.

### Observed (2026-06-30, L'Usine Work Bot)

| Time | Event |
|------|-------|
| 08:11:18 | ✅ Bot processed `[col]` message successfully |
| 08:13:00 | ❌ WinError 64 — TCP drop |
| 08:13:11 | 🔄 Bot reconnected (logged "Connection established") |
| **Post-08:13** | **Bot process exited** — no longer running |

Symptom: bot stops responding to ALL messages (`[col]`, `[new case]`, etc.). No new ERROR logs — the process simply vanished.

### Root Cause Not Fully Understood

The WinError 64 + reconnect happens regularly and the bot keeps running. **This specific instance may be an edge case** — possibly the process crashed during the next polling cycle after reconnect, or was killed by an external factor (OS update, memory pressure, etc.).

### Mitigation: Process Health Check

When the user reports "bot không phản hồi", the **first diagnostic step** is checking process liveness:

```bash
wmic process where "name='python.exe'" get ProcessId,CommandLine | findstr "lusine_ops.telegram_bot"
```

- **Empty result** → bot process is dead → restart
- **Result found** → bot is running but not processing → handler/queue issue (different debugging path)

### Auto-Restart Setup (Recommended)

The `.bat` launcher already has an auto-restart loop:

```bat
:loop
echo [%date% %time%] Starting bot...
python.exe -m lusine_ops.telegram_bot
echo [%date% %time%] Bot stopped. Restarting in 5s...
timeout /t 5 >nul
goto loop
```

**Verify launch method** — if the bot is run directly via `python -m lusine_ops.telegram_bot` instead of through the `.bat`, it won't auto-restart. Check with the user which launch method they use.
