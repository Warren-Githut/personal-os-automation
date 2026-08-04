# WinError 64 — Transient Network Error (Windows)

> Cross-reference: detailed version with code fix lives at `telegram-bot-integration/references/windows-winerror64-aiogram.md`

## Quick Diagnosis

**Symptom:** `ClientOSError: [WinError 64] The specified network name is no longer available` in aiogram polling logs.

**Recovery pattern (self-healing):**
```
08:13:00 | ERROR    | Failed to fetch updates - ...ClientOSError: [WinError 64] ...
08:13:00 | WARNING  | Sleep for 1.000000 seconds and try again...
08:13:11 | INFO     | Connection established
```

## Triage

| Pattern | Verdict |
|---------|---------|
| Error → retry WARNING → reconnect INFO in <15s | ✅ **Transient, self-healing** — ignore |
| Error persists across multiple retries >30s | 🔴 **Persistent network issue** — check firewall, WiFi, VPN |

## Fix (Logging Filter)

Add before the bot's main polling loop:

```python
class TransientNetworkFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if "WinError 64" in record.getMessage() and record.levelno >= logging.ERROR:
            record.levelno = logging.WARNING
            record.levelname = "WARNING"
        return True

logging.getLogger("aiogram").addFilter(TransientNetworkFilter())
```

This downgrades WinError 64 ERROR/CRITICAL → WARNING without changing retry behavior.
