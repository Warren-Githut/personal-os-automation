# Cross-Profile mem0 Inspection — 2026-06-25 Session

## Context

All 4 Warren profiles share the same Qdrant server (`localhost:6333`, 768-dim vectors, `mem0` collection). Each profile uses a different `user_id` in its `mem0.json`, which Qdrant treats as a partition key.

## Qdrant Collection State

- Collection: `mem0`
- Total points: **31** (as of 2026-06-25T13:xx)
- Backend: Docker Qdrant (`localhost:6333`)

## Per-Profile Breakdown

| Profile | user_id | Memories | Quality |
|---|---|---|---|
| stock-profile | `warren_stock` | **30** | ~50% noise (chat artifacts, status lines) |
| personal_profile | `warren_personal` | **1** | Clean (health log) |
| warren-profile | `warren` | **0** | Configured but never used |
| lusine-profile | (no mem0.json) | **0** | Not configured |

## Payload Structure

Each Qdrant point has these fields:

```json
{
  "user_id": "warren_stock",
  "agent_id": "hermes",
  "channel": "tui",
  "data": "<stored memory text>",
  "text_lemmatized": "<same>",
  "hash": "<md5>",
  "created_at": "2026-06-25T13:19:43.327925+00:00",
  "updated_at": "2026-06-25T13:19:43.327925+00:00",
  "attributed_to": "assistant"
}
```

## Stock-Profile Signal vs Noise Analysis

### High-signal (durable knowledge)

- DRC: Cao su Đà Nẵng, doanh nghiệp thật, P/E hợp lý
- TNG: dệt may tư nhân #1 miền Bắc, DT 2025 kỷ lục 8.699 tỷ, 5T/2026 +23%
- Catalyst: 24/07/2026 đàm phán thuế Mỹ
- P/E 5,9x — rẻ hơn lịch sử 7,5x, nhưng đòn bẩy ~1,7x VCSH là red flag
- Cổ tức 20% tiền mặt → yield ~11%
- Skill architecture: canonical at warren-profile, hard links from stock-profile
- Cross-profile guard redirects writes to warren-profile
- Đừng quên kiểm tra HNX/UPCOM (không có trên Yahoo)
- Warren uses TCBS, cross-check VPS + HSC

### Low-signal (chat artifacts / transient)

- "mem0 status — ALL GREEN"
- "Xong. Đây là kết quả cuối"
- "KHÔNG TÌM THẤY"
- "Rồi — đây là kết quả:"
- "user: cái này nên lưu vào đâu"
- Component tables (Ollama OK, Qdrant OK, Config OK)
- RSI scan results (stale after market moves)
- "assistant: Xong. Đà tạo đưng ădd Đõ..." (corrupted text)
- "20260625_101813_51ff58 check lịch sử nhé" (session noise)
- "File PDF vẫn nằm ở Desktop. Muốn tôi move..." (one-off query)
- "TCBS Initiation TNG — single-company broker report" (metadata, not content)
- "user: fetch_financials.py nằm trong stock-profile/skills/" (should be an action)

### Key Discovery

mem0 OSS stores **everything** that is automatically saved or explicitly added — it does not filter for signal. The `attributed_to` field can help distinguish:
- `assistant` → auto-saved by the mem0 plugin during conversation
- `user` → user's own messages (often requests or commands, not knowledge)

## Commands Used

```bash
# Count points
curl -s http://localhost:6333/collections/mem0 | python3 -c "import json,sys; r=json.load(sys.stdin)['result']; print(r['points_count'])"

# Full scroll with payload
curl -s -X POST 'http://localhost:6333/collections/mem0/points/scroll' \
  -H 'Content-Type: application/json' \
  -d '{"limit":100,"with_payload":true,"with_vector":false}'

# Group by user_id
# (see inline Python script in SKILL.md section "Data Inspection")
```
