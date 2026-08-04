# Cross-Profile Mem0 Write via Qdrant REST API

## Problem

Ghi mem0 vào personal_profile (`user_id: warren_personal`) hoặc stock-profile (`user_id: warren_stock`) từ warren-profile session. Hermes `mem0_add` tool không có profile parameter — chỉ ghi vào profile hiện tại.

## Why Not `Memory.from_config()`

mem0ai v2.0.7 có bug: khi embedder provider là Ollama, factory vẫn tạo OpenAI client và fail với:
```
Missing credentials. Please pass an `api_key`
```

**Solution:** Skip mem0 library hoàn toàn — ghi trực tiếp vào Qdrant REST API.

## Workflow (verified 2026-06-28)

### 1. Get embedding từ Ollama

```python
import requests

r = requests.post("http://localhost:11434/api/embeddings", json={
    "model": "nomic-embed-text",
    "prompt": "text to embed"
})
vec = r.json()["embedding"]
```

### 2. Write point to Qdrant

```python
import uuid

point_id = str(uuid.uuid4())
payload = {
    "user_id": "warren_personal",  # or "warren_stock"
    "agent_id": "hermes",
    "text": fact_text,
    "metadata": {},
    "memory": fact_text,
}

r = requests.put("http://localhost:6333/collections/mem0/points", json={
    "points": [{
        "id": point_id,
        "vector": vec,
        "payload": payload,
    }]
})
```

### 3. Verify

```bash
# Search by user_id
curl -s -X POST 'http://localhost:6333/collections/mem0/points/search' \
  -H 'Content-Type: application/json' \
  -d '{"vector": [...], "limit": 1, "with_payload": true,
       "filter": {"must": [{"key": "user_id", "match": {"value": "warren_personal"}}]}}'
```

## Profile user_id mapping

| Profile | user_id |
|---------|---------|
| warren-profile | `warren` |
| personal_profile | `warren_personal` |
| stock-profile | `warren_stock` |

All 3 profiles share the same Qdrant instance at `http://localhost:6333`, same collection `mem0`, same embedder `nomic-embed-text` (768 dims).

## When to use

- Bạn đang ở profile A nhưng cần ghi fact vào mem0 của profile B
- `Memory.from_config()` fail vì bug embedder factory
- Cần bulk write/copy memories giữa các profiles

## Script pattern

Xem `warren-profile/scripts/mem0_cross_profile_add.py` — script đã verified cho cả personal + stock.
