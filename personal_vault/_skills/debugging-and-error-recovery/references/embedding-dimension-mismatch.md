# Embedding Dimension Mismatch in Vector Stores

## Symptom

```
ValueError: shapes (0,1536) and (768,) not aligned: 1536 (dim 1) != 768 (dim 0)
```

The vector store collection was created with **1536 dimensions** (OpenAI default), but your embedder produces **768** (e.g., `nomic-embed-text`) or **1024** (e.g., `bge-m3`). The `cosine_similarity` / `np.dot` call fails because the query vector and stored vectors have different shapes.

## Root Cause

Two layers of a memory/vector-store framework disagree on the embedding dimension:

1. **Embedder config** has `embedding_dims` set correctly (e.g., 768 for `nomic-embed-text`).
2. **Vector store config** has `embedding_model_dims` defaulting to **1536** (OpenAI default in most frameworks: Mem0, LangChain, Qdrant, Chroma — all ship with 1536 as the baked-in default).

The framework **does not propagate** the embedder's actual dimension to the vector store's collection-creation parameter. The collection is created with 1536, but the embedder returns 768 → mismatch.

**Frameworks with this bug:**
- Mem0 — [Issue #4695](https://github.com/mem0ai/mem0/issues/4695) (confirmed, closed "not planned — workaround exists")
- Any vector-store library that separates embedder config from vector-store config without sync logic

## Reproduction

```python
from mem0 import Memory

config = {
    "vector_store": {
        "provider": "qdrant",
        "config": {"path": "./qdrant_data", "embedding_model_dims": 768},  # Set here
    },
    "embedder": {
        "provider": "ollama",
        "config": {"model": "nomic-embed-text", "embedding_dims": 768},  # And here
    },
    # ...
}
m = Memory.from_config(config)
m.add("test", user_id="x")  # Still crashes with 1536 mismatch
```

Both configs explicitly set 768, but the vector store ignores it because the `embedding_model_dims` from the config dict is not passed to the Qdrant constructor.

## Fix

Patch the framework's `Memory.__init__()` to sync dimensions **after** the embedder is created and **before** the vector store is created:

```python
# In mem0/memory/main.py, class Memory.__init__(), around line 415:
self.embedding_model = EmbedderFactory.create(
    self.config.embedder.provider,
    self.config.embedder.config,
    self.config.vector_store.config,
)
# >>> PATCH: sync actual embedding dims to vector store config <<<
actual_dims = getattr(self.embedding_model.config, 'embedding_dims', None)
if actual_dims and hasattr(self.config.vector_store.config, 'embedding_model_dims'):
    self.config.vector_store.config.embedding_model_dims = actual_dims
# >>> END PATCH <<<
self.vector_store = VectorStoreFactory.create(
    self.config.vector_store.provider, self.config.vector_store.config
)
```

Apply the same patch to `AsyncMemory.__init__()` if it exists.

## Prevention

- After the fix: delete the old collection (wrong dims) before creating a new one:
  ```bash
  rm -rf ~/.mem0  # Only if you don't need existing data
  # Or just the collection directory:
  rm -rf /path/to/qdrant/storage/collection_name
  ```
- Test with `m.add()` + `m.search()` before assuming the fix works.

## Windows-Specific: Qdrant Local Lock Conflict

When testing multiple `Memory` instances in the same Python process, Qdrant local mode on **Windows** will crash with:

```
RuntimeError: Storage folder C:\Users\xxx\.mem0\migrations_qdrant
is already accessed by another instance of Qdrant client.
```

**Cause:** Mem0 creates a telemetry vector store at `~/.mem0/migrations_qdrant`. Qdrant local uses `portalocker` with `msvcrt.locking()` (Windows native file locking). When `Memory.close()` is called, the Python reference is released but the OS file lock may **not** be released until the process exits. The second `Memory()` instance finds the telemetry folder locked.

**Workarounds:**
1. **Test one Memory instance per process** — use `subprocess.run([sys.executable, "-c", code])` to isolate each test in its own process (lock released when process exits).
2. **Delete the telemetry folder** between instances:
   ```python
   shutil.rmtree(os.path.expanduser("~/.mem0/migrations_qdrant"), ignore_errors=True)
   ```
   (May not always work — the lock file may survive `rmtree` on Windows.)
3. **Use Qdrant server mode** instead of local — run `docker run -p 6333:6333 qdrant/qdrant` and connect via `host: "localhost", port: 6333`.

**This does not affect production** — each Hermes profile runs as its own process, so no two instances ever share the telemetry folder.

## Related: Mem0 v2 API Change

Mem0 v2 changed `search()` to require `filters` as a dict instead of top-level `user_id=`:

```python
# Mem0 v1 (broken in v2):
m.search("query", user_id="alice")

# Mem0 v2:
m.search("query", filters={"user_id": "alice"})
```

If you get `TypeError: Top-level entity parameters frozenset({'user_id'}) are not supported`, this is the cause.
