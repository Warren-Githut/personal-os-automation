# 3-Profile Consistent Mem0 Setup (2026-06-25)

## Architecture

All 3 profiles use **embedded Qdrant** (path-based, `on_disk: true`) + **Ollama** for LLM + embeddings.
No Docker dependency. Each profile has isolated memory via unique `user_id` and separate Qdrant path.

## The 3 Profiles

| Profile | user_id | Qdrant path | LLM |
|---|---|---|---|
| `stock-profile` | `warren_stock` | `~/.hermes/qdrant/stock_profile/` | ollama/llama3.2:3b |
| `warren-profile` | `warren` | `~/.hermes/qdrant/warren/` | ollama/llama3.2:3b |
| `personal_profile` | `warren_personal` | `~/.hermes/qdrant/personal/` | deepseek/deepseek-chat |

## Config Files

### stock-profile `mem0.json`
```
C:/Users/khoans/AppData/Local/hermes/profiles/stock-profile/mem0.json
```
```json
{
  "mode": "oss",
  "user_id": "warren_stock",
  "agent_id": "hermes",
  "oss": {
    "llm": {
      "provider": "ollama",
      "config": {
        "model": "llama3.2:3b",
        "ollama_base_url": "http://localhost:11434",
        "temperature": 0.2,
        "max_tokens": 2000
      }
    },
    "embedder": {
      "provider": "ollama",
      "config": {
        "model": "nomic-embed-text",
        "ollama_base_url": "http://localhost:11434",
        "embedding_dims": 768
      }
    },
    "vector_store": {
      "provider": "qdrant",
      "config": {
        "path": "C:/Users/khoans/.hermes/qdrant/stock_profile",
        "embedding_model_dims": 768,
        "on_disk": true
      }
    }
  }
}
```

### warren-profile `mem0.json`
```
C:/Users/khoans/AppData/Local/hermes/profiles/warren-profile/mem0.json
```
Same structure, different `user_id: "warren"` and `path: ".../qdrant/warren"`.

### personal_profile `mem0.json`
```
C:/Users/khoans/AppData/Local/hermes/profiles/personal_profile/mem0.json
```
Same structure, different:
- `user_id: "warren_personal"`
- `path: ".../qdrant/personal"`
- LLM: `deepseek/deepseek-chat` (requires `api_key` in config)

## Key Paths

All mem0.json files live in `~/AppData/Local/hermes/profiles/<profile>/mem0.json`.
All Qdrant databases live in `~/.hermes/qdrant/<name>/collection/`.

## Verification Script

`mem0-status.sh` at `~/AppData/Local/hermes/profiles/stock-profile/scripts/mem0-status.sh`
Registered as quick command: `hermes quick mem0-status`

Checks:
- Ollama reachable at localhost:11434
- Embedded Qdrant paths exist for all 3 profiles
- Prints user_id + path per profile

## Migration Note

Stock-profile was migrated from Docker Qdrant (HTTP) to Embedded Qdrant on 2026-06-25.
10 points of old data in Docker Qdrant `mem0` collection were orphaned (all debug responses + 2-3 user facts also stored in built-in memory).
