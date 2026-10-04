# Qdrant Embedded Concurrent Access — Root Cause Analysis

**Date:** 2026-06-25  
**Session:** Hermes warren-profile, ops-col debug  
**Symptom:** Mem0 error `Storage folder already accessed by another instance of Qdrant client` — recurring across sessions despite `.lock` cleanup.

---

## Process Map at Time of Failure

```
PID 6868  — hermes dashboard (generic)
PID 10688 — hermes dashboard (generic, uv python)
PID 12108 — hermes dashboard (warren-profile)
PID 18920 — hermes dashboard (warren-profile, uv python)
PID 11996 — Telegram bot (lusine_ops.telegram_bot, Python312)
PID 19120 — slash_worker (session 20260625_154317, deepseek-v4-pro)
PID 20204 — slash_worker (session 20260625_154317, uv python)
PID 19216 — slash_worker (session 20260625_152211, deepseek-v4-pro)
PID 12616 — slash_worker (session 20260625_152211, uv python)
```

**6 distinct Hermes processes** + Telegram bot = 7 processes that could initialize Mem0 with the same Qdrant embedded path.

---

## Why Deleting `.lock` Doesn't Fix It

1. Delete `.lock` → temporary relief
2. Another process (cron job, slash worker) initializes Mem0 → creates new `.lock`
3. Our process tries to use Mem0 → locked again

This is NOT a stale lock from a crashed process. It's a **live lock conflict** between concurrently running processes.

---

## Architecture Gap

| Component | Expectation | Reality |
|-----------|------------|---------|
| Qdrant Embedded | Single-process access | 7+ processes trying to access |
| Hermes Mem0 Plugin | One init per process | All processes share same storage path |
| `.lock` file | Prevent data corruption | Prevents ALL access from non-owner processes |

---

## Solution: Qdrant Server (Docker)

Qdrant server supports concurrent connections from multiple clients. Each Hermes process connects to the server independently.

```bash
# Start Qdrant server
docker run -d --name qdrant -p 6333:6333 --restart unless-stopped qdrant/qdrant

# Verify
curl http://localhost:6333/healthz
```

**mem0.json change:**
```json
"vector_store": {
    "provider": "qdrant",
    "config": {
        "url": "http://localhost:6333",     // ← was "path": "C:/Users/..."
        "embedding_model_dims": 768
    }
}
```

**Data migration needed:** Existing embedded data at `~/.hermes/qdrant/warren/collection/` must be re-ingested or re-created. Qdrant Docker starts fresh.

---

## Alternative: Isolated Paths Per Profile

If Docker is not available, use different storage paths per process. But this fragments memory data — searches from one session won't find memories from another.

```json
// warren-profile/mem0.json
"path": "C:/Users/khoans/.hermes/qdrant/warren"

// stock-profile/mem0.json  
"path": "C:/Users/khoans/.hermes/qdrant/stock"
```

This works for separate profiles but doesn't solve the multi-process-within-same-profile problem (dashboard + slash worker both use `warren` path).

---

## Status (2026-06-25)

- **warren-profile:** Embedded Qdrant, `.lock` conflict when multiple Hermes processes run
- **stock-profile:** Embedded Qdrant, separate path — less likely to conflict (only 1 profile's processes)
- **personal_profile:** Embedded Qdrant, separate path — same

**Recommendation:** Migrate warren-profile to Qdrant Docker server. Leave stock/personal on embedded (they have fewer concurrent processes).
