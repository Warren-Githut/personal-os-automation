# Stock Profile: mem0 OSS Setup — 2026-06-24

## Profile Context

- Profile: `stock-profile`
- HERMES_HOME: `C:\Users\khoans\AppData\Local\hermes\profiles\stock-profile`
- mem0.json path: `C:\Users\khoans\AppData\Local\hermes\profiles\stock-profile\mem0.json`
- OS: Windows 10, bash via git-bash

## Docker

- Already installed: Docker Desktop v29.4.2, build 055a478
- Docker daemon was NOT running at session start
- Started via running `com.docker.backend.exe` (took ~30s to initialize)
- Qdrant pulled: `docker pull qdrant/qdrant` (~20s)
- Qdrant started: `docker run -d --name qdrant -p 6333:6333 qdrant/qdrant`

## Python Packages

- Venv: `C:\Users\khoans\AppData\Local\hermes\hermes-agent\venv`
- Python: 3.11.15
- pip: 24.0
- **Installed**: `mem0ai v2.0.7`, `qdrant-client v1.18.0`, `ollama v0.6.2`
- PyPI search: `mem0` → not found. Correct name is `mem0ai`.

## Ollama

- Version: 0.30.10
- Pre-installed models:
  - llama3.2:3b (3.2B, Q4_K_M)
  - tinyllama:latest (1B)
  - nomic-embed-text (137M, F16, 768 dims)
- API available at `http://localhost:11434`

## Config Mistake Avoided

First attempt used `hermes config set mem0.qdrant_url http://localhost:6333` — this writes to config.yaml's `mem0:` block which the Hermes mem0 plugin **does not read**. The plugin loads config from `$HERMES_HOME/mem0.json` via `_load_config()`.

The `mem0:` block in config.yaml is for platform-mode fallback only. For OSS mode, all config goes in `mem0.json`.

## Dimension Matching Saga

1. First test: mem0 created Qdrant collection with default 1536 dims (OpenAI default)
2. nomic-embed-text produces 768 dim vectors
3. Error: `"Vector dimension error: expected dim: 1536, got 768"`
4. Fixed by adding `"embedding_model_dims": 768` to vector_store.config AND deleting old collection
5. After fix: collection dim=768, Cosine distance. Verified.

The `embedding_model_dims` must be in `config["vector_store"]["config"]`, NOT top-level config.

## Performance

- mem0 init: ~3s
- First `add()` with fact extraction (ollama llama3.2:3b): **197s** (~3 minutes)
- All subsequent operations: faster (warm cache)
- Search: ~5s (embedding + vector search)

All mem0 operations run in Hermes background threads — agent not blocked.

## Final Verification

```python
# Qdrant collections
mem0: dim=768, distance=Cosine, points=4
mem0migrations: dim=768, distance=Cosine, points=0

# Search returned 4 extracted facts from 1 input sentence
# - "User uses TCBS for stock trading"
# - "User cross-checks with VPS and HSC"
```

## Cross-Profile Audit — 2026-06-25

This session audited mem0 across all 4 Hermes profiles.

### Profile Inventory

```
~/AppData/Local/hermes/profiles/
├── lusine-profile/     ❌ no config.yaml, no mem0.json
├── personal_profile/   ✅ embedded Qdrant, user_id=warren_personal
├── stock-profile/      ✅ Docker Qdrant (HTTP), user_id=warren_stock
└── warren-profile/     ✅ embedded Qdrant, user_id=warren
```

### Key Observations

1. **Embedded vs Docker Qdrant**: Two architectures coexist. Embedded (`path` + `on_disk: true`) is more robust (no Docker dependency). Stock-profile uses Docker HTTP (`url: http://localhost:6333`).

2. **Config location confusion**: Hermes app config lives in `~/AppData/Local/hermes/` (not `~/.hermes/`). The `~/.hermes/` directory exists but is for Qdrant data storage, not config.

3. **Skills symlink**: stock-profile's `skills/` dir is a symlink → `warren-profile/skills/`. All skill updates happen in warren-profile's skill tree.

4. **Docker Qdrant status (during audit)**: `docker ps` → Qdrant was running "Up 3 minutes". Only `mem0` and `mem0migrations` collections exist.

### Profile Config Quick Check Command

```bash
for p in ~/AppData/Local/hermes/profiles/*/; do
  name=$(basename "$p")
  echo "=== $name ==="
  grep "provider: mem0" "$p/config.yaml" 2>/dev/null && echo "  ✅ mem0" || echo "  ❌ no mem0"
  [ -f "$p/mem0.json" ] && echo "  ✅ mem0.json" || echo "  ❌ no mem0.json"
done
```

### Fix Needed

- **lusine-profile**: completely missing. Needs config.yaml + mem0.json to activate mem0.
- **Stock-profile embedded migration**: optionally switch from Docker Qdrant to embedded Qdrant for consistency with other profiles.

