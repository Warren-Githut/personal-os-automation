# mem0 backends — swap vs remove (Warren 2026-07-08)

## Architecture fact (verified from `mem0.json`, warren-profile)
mem0 OSS mode depends on TWO local servers:
- **vector_store** → Qdrant `http://localhost:6333` (the heavy one Warren dislikes)
- **llm + embedder** → Ollama `http://localhost:11434` (llama3.2:3b extract, nomic-embed-text embed)

## Two distinct decisions
| Decision | Meaning | Effort | Risk |
|---|---|---|---|
| **Swap backend** (Option A, CHOSEN) | Keep mem0 layer, change `vector_store.provider` qdrant→lancedb. Ollama stays. | ~2h | Low (config-only) |
| **Remove layer** (Option C) | Drop mem0 entirely, rebuild memory on zvec/Tencent. | days | High |

## Backend options mem0 supports (docs.mem0.ai)
Qdrant, Chroma, PGVector, Pinecone, Milvus, **LanceDB**, in-memory.
- LanceDB = embedded/serverless, Windows OK, native mem0 support → recommended swap.
- sqlite-vec = lightest but NO official mem0 connector → needs custom VectorStore class.
- zvec (Alibaba) = engine, no mem0 connector yet → only if building custom layer.

## Tencent Agent Memory (github.com/TencentCloud/TencentDB-Agent-Memory)
- Has OFFICIAL Hermes adapter (`hermes-plugin/memory/memory_tencentdb`, `Dockerfile.hermes`).
- SQLite local, no server, L0-L3 layering matches vault philosophy (WARREN_MEMORY=Persona, sessions=raw).
- Decision: evaluate ISOLATED later, not as mem0 replacement yet (avoid mid-flight flip).

## Cron dependencies (verified)
`mem0-cleanup-warren` (Sun 09:00) + `mem0-30day-review` (2026-07-24) use mem0 API, NOT Qdrant directly → survive backend swap.
