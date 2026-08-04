# Qdrant Local + Windows: Portalocker Lock Conflict

## Symptom

When creating a second `Memory()` instance in the same Python process on Windows:

```
RuntimeError: Storage folder C:\Users\xxx\.mem0\migrations_qdrant
is already accessed by another instance of Qdrant client.
```

## Root Cause

- Mem0 creates a **telemetry vector store** at `~/.mem0/migrations_qdrant` inside every `Memory.__init__()`.
- Qdrant local mode uses `portalocker` with `msvcrt.locking()` (Windows native file locking).
- `Memory.close()` releases the Python reference, but the **OS file lock** is only released when the **process** exits.
- Any second `Memory()` instance in the same process finds the telemetry folder locked.

## Detection

- Always check `~/.mem0/migrations_qdrant` when you see Qdrant-related `RuntimeError` or `PermissionError` on Windows.
- The error trace goes: `Memory.__init__()` → `_telemetry_vector_store` → `VectorStoreFactory.create()` → `QdrantClient` → `QdrantLocal._load()` → `portalocker.lock()` → `msvcrt.locking()` → `PermissionError`.

## Workarounds

| Approach | Works? | Notes |
|----------|--------|-------|
| `shutil.rmtree("~/.mem0/migrations_qdrant")` + `time.sleep(0.5)` | ⚠️ Sometimes | Lock file may survive `rmtree` on Windows |
| **subprocess isolation** | ✅ Always | Each test in its own `subprocess.run([sys.executable, "-c", code])` |
| Use Qdrant server (Docker) | ✅ | `docker run -p 6333:6333 qdrant/qdrant` |
| Same process, one instance | ✅ | Don't create a second Memory — reuse the first |

## Practical Impact

**Zero in production.** Each Hermes profile runs as its own process (`hermes` CLI invocation), so no two `Memory()` instances ever share the telemetry folder. This only bites during in-process testing or when running multiple tests in a single Python script.

**For test code:** prefer `subprocess.run()` with `-c` for each isolation-sensitive test. Add `import shutil, os; shutil.rmtree(os.path.expanduser("~/.mem0/migrations_qdrant"), ignore_errors=True)` between tests as a best-effort cleanup.

## References

- [portalocker issue](https://github.com/WoLpH/portalocker) — Windows-specific locking behavior
- Mem0 `_backend.py` OSSBackend — the Hermes plugin that creates isolated Memory instances per profile
