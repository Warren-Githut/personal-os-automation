# On-Demand Lightweight mem0 — 2026-06-27

## Context

Warren muốn dùng mem0 nhưng không muốn Qdrant + Ollama chạy 24/7 (tốn RAM ~500MB-3GB). Giải pháp: tắt mem0 auto (`provider: ''`), chỉ bật khi cần, tắt ngay sau khi dùng.

## Files created/updated

### Desktop (cho Warren double-click)

```
Desktop\
├── mem0.ps1        ← Engine chính (PowerShell)
├── mem0-on.bat     ← Thin wrapper: gọi powershell -File mem0.ps1 -Action On
└── mem0-off.bat    ← Thin wrapper: gọi powershell -File mem0.ps1 -Action Off
```

### Profile scripts (cho Hermes terminal)

```
%LOCALAPPDATA%\hermes\profiles\warren-profile\scripts\
├── mem0.ps1
├── mem0-on.bat
└── mem0-off.bat
```

### Wiki (trong vault)

```
vault/30_KNOWLEDGE_BASE/wiki/Mem0_Manual_Flow.md
```

## Why PowerShell over batch (.bat)

1. **Start-Process** runs background services đúng cách (không bị MSYS path conversion)
2. **Invoke-RestMethod** tạo Qdrant collections chính xác — không bị curl escaping issue trong cmd.exe
3. **Stop-Process -Force** kill process sạch sẽ
4. **error handling** try/catch rõ ràng hơn ERRORLEVEL

## Key learnings

### Qdrant 1.18 native Windows

| What | Detail |
|------|--------|
| No `--storage-path` | Removed in 1.18, use `--config-path` instead |
| Health endpoint | `GET /` (root), not `/healthz` (Docker-only) |
| Config | `storage.storage_path` must be **absolute path** |
| Why absolute | Working directory unpredictable with Start-Process. Relative `storage_path: .` may resolve to Desktop or System32 |

### Auto-create collections

mem0 OSS expects collections `mem0` + `mem0_entities` (768-dim Cosine, BM25 sparse). If Qdrant starts fresh (no data), `mem0_add` fails with:
```
404: Collection `mem0` doesn't exist!
```

Script auto-creates via REST API:
```powershell
$body = @{vectors=@{size=768; distance="Cosine"}; sparse_vectors=@{bm25=@{modifier="idf"}}} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:6333/collections/mem0" -Method Put -Body $body -ContentType "application/json"
```

### 3 cách dùng (Warren preference ranking)

1. **Cách C** — Nói Hermes làm hết (không rời tay, ưu tiên):
   ```
   Warren: "mem0 ơi, bật giúp tôi nhớ là ..."
   Agent: terminal(mem0-on) → mem0_add → terminal(mem0-off)
   ```
2. **Cách A** — Double-click .bat trên Desktop
3. **Cách B** — PowerShell command line

### Config changes

All 3 profiles: `provider: mem0` → `provider: ''` (tắt auto-init)

```
%LOCALAPPDATA%\hermes\profiles\warren-profile\config.yaml
%LOCALAPPDATA%\hermes\profiles\stock-profile\config.yaml  
%LOCALAPPDATA%\hermes\profiles\personal_profile\config.yaml
```

mem0.json for each profile kept intact — used when services are running.

### Built-in memory khuyên dùng cho daily use

| Feature | Built-in memory | mem0 (on-demand) |
|---------|----------------|-------------------|
| RAM | 0 | ~100MB when on, 0 when off |
| Semantic search | No | Yes |
| Need to start services | No | Yes (Qdrant + Ollama) |

Use built-in `memory` tool for quick notes/preferences. Fire up mem0 only for important facts that need vector search later.

## Verified round-trip (2026-06-27)

```
Powershell mem0.ps1 -Action On → Qdrant ready + Ollama ready
mem0_add("Warren thích đầu tư vào cổ phiếu GAS nhiều lắm") → "Fact stored."
mem0_search("Warren thích cổ phiếu gì?") → score 0.84, text found
Powershell mem0.ps1 -Action Off → both stopped
```
