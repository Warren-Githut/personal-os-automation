# Mem0 Setup Reference — Hermes External Memory Provider

> Source: Research session 2026-06-24 — PR #50479 + Mem0 docs + configuration analysis.
> Applies to: warren-profile, personal_profile, stock-profile, any future profile.

---

## Architecture Overview

```
Hermes Agent
    │
    ├── Built-in Memory (SQLite FTS5)
    │   ├── MEMORY.md (~2,200 chars) — agent's personal notes
    │   ├── USER.md (~1,375 chars) — user profile
    │   └── session_search (conversation history)
    │
    └── External Provider: Mem0 (additive, not replacement)
        ├── LLM: DeepSeek v4 Flash (fact extraction)
        ├── Embedder: Ollama nomic-embed-text (vector generation)
        └── Vector Store: Qdrant local (/tmp/qdrant)
```

## Installation

### 1. Library (1 lệnh duy nhất)
```bash
pip install mem0ai qdrant-client
```

### 2. Config (Python)

**Option A — DeepSeek LLM + Ollama embedder** (faster extraction, needs valid API key):
```python
from mem0 import Memory

config = {
    "llm": {
        "provider": "deepseek",
        "config": {
            "model": "deepseek-chat",
            "temperature": 0.2,
            "max_tokens": 2000,
            "top_p": 1.0,
            "api_key": "sk-..."     # ✅ REQUIRED — DeepSeek is cloud API
        }
    },
    "embedder": {
        "provider": "ollama",
        "config": {
            "model": "nomic-embed-text",
            "ollama_base_url": "http://localhost:11434"
        }
    }
}

m = Memory.from_config(config)
```

**⚠️ Important:** The Hermes proxy at `localhost:8787` does NOT apply to mem0 — mem0 calls DeepSeek directly. The `DEEPSEEK_API_KEY` env var in `.env` may NOT be inherited by the Hermes agent process. Safest: pass `api_key` explicitly in `mem0.json`.

**Option B — Ollama-only** (slower ~3 min first write, zero external dependency, no API key needed):
```python
config = {
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
            "ollama_base_url": "http://localhost:11434"
        }
    }
}
```

**Nếu muốn dùng OpenAI embeddings (nhanh hơn, $0.02/tháng):**
```python
# Set OPENAI_API_KEY env var
config["embedder"] = {
    "provider": "openai",
    "config": {
        "model": "text-embedding-3-small"
    }
}
```

### 3. Hermes Plugin Activation
```bash
hermes memory setup     # interactive → chọn mem0
hermes memory status    # verify active
```

Plugin tự tạo `$HERMES_HOME/mem0.json` và wire các tools:
- `mem0_list`, `mem0_search`, `mem0_add`, `mem0_update`, `mem0_delete`

## Key Config Parameters

### Per-profile JSON (`$HERMES_HOME/mem0.json`)
```json
{
  "mode": "oss",
  "user_id": "warren",
  "agent_id": "hermes",
  "host": "http://localhost:8000",    // only for self-hosted server mode
  "api_key": null,                    // not needed for library mode
  "rerank": false,
  "top_k": 10
}
```

### Environment Variables
| Var | Purpose | Default |
|-----|---------|---------|
| `DEEPSEEK_API_KEY` | LLM for fact extraction | Required |
| `OPENAI_API_KEY` | Embedder (if using OpenAI) | Optional |
| `MEM0_HOST` | Self-hosted server URL (PR #50479) | `https://api.mem0.ai` |
| `OLLAMA_BASE_URL` | Ollama embedder endpoint | `http://localhost:11434` |

## Cross-Profile Memory Strategy

| Strategy | Config | Behavior |
|----------|--------|----------|
| **Shared memory** | All profiles → same Qdrant host + collection | warren-profile sees personal_profile memories (and vice versa) |
| **Isolated memory** | Each profile has own `mem0.json` pointing to different databases | Zero cross-contamination |
| **Hybrid** | Shared for domain-agnostic facts, separate for domain-specific | Most flexible but complex |

**For Warren's setup (warren-profile + personal_profile + stock-profile):**
- Default: **isolated** — mỗi profile có vector store riêng
- Có thể chuyển sang shared sau nếu muốn cross-domain memory

## Library Mode vs Server Mode

| Aspect | Library (recommended) | Server (Docker) |
|--------|-----------------------|-----------------|
| Install | `pip install mem0ai` | `docker compose up` (3 containers) |
| Dependencies | Python + Qdrant local | Docker + Neo4j + PostgreSQL + pgvector |
| RAM | ~100MB | ~512MB-1GB |
| Dashboard | None | Web UI at port 3000 |
| Use case | Single user, local laptop | Team, production, multi-agent |

## How Memory Extraction Works

```
User: "Tôi thích báo cáo kết luận trước"
    │
    ▼
Mem0 LLM (DeepSeek) extract fact:
    → "Warren prefers conclusion-first report format"
    │
    ▼
Embedder (Ollama) → vector (768-dim)
    │
    ▼
Qdrant: lưu vector + text
    │
    ▼
Neo4j: lưu entity graph
    [Warren] --prefers--> [conclusion-first format]
    [Warren] --receives--> [reports]

Later: "Format nào tôi muốn?"
    → search vector → nearest match: "conclusion-first report format" [score: 0.89]
```

## Known Issues & Gotchas

- **Embedder is separate from LLM** — DeepSeek supports chat LLM but NOT embeddings. Must configure independent embedder (Ollama or OpenAI).
- **Python vs TypeScript config keys differ:** Python uses `openai_base_url` / `api_key` (snake_case), TypeScript uses `baseURL` / `apiKey` (camelCase). Mixing them causes silent fallback to default OpenAI endpoint → 401 errors.
- **PR #50479** adds `MEM0_HOST` env var and `host` config key — merged into main 2026-06-22. Needed for self-hosted server mode only. Library mode (pip install) does NOT need this.
- **Qdrant default path:** `/tmp/qdrant` — không persist qua reboot. Cần mount ổn định cho production.

## Benchmarks

| Benchmark | Mem0 v3 score | Notes |
|-----------|---------------|-------|
| LongMemEval | 94.8% | Long-term memory retrieval |
| LoCoMo | 91.6% | Conversation memory |
| BEAM (1M) | 64.1% | Large-scale retrieval |
| BEAM (10M) | 48.6% | At scale |
| Tokens per operation | ~6.8K | Fact extraction + embedding |

## Quick Test

```python
from mem0 import Memory
import os

os.environ["DEEPSEEK_API_KEY"] = "sk-..."
# Set OLLAMA_BASE_URL if using Ollama embedder

m = Memory.from_config({...})  # see config above

# Add
m.add([
    {"role": "user", "content": "Tôi thích báo cáo kết luận trước, dẫn chứng sau."},
    {"role": "assistant", "content": "OK, tôi sẽ nhớ format này."}
], user_id="warren")

# Search
results = m.search("Warren thích format báo cáo nào?", user_id="warren")
print(results["results"][0]["memory"])
# → "Warren prefers conclusion-first, evidence-second format"

# List all (⚠️ mem0 v2.0.7+: use filters={} not top-level params)
all_mem = m.get_all(filters={'user_id': 'warren'})
print(f"Total: {len(all_mem)}")
```
