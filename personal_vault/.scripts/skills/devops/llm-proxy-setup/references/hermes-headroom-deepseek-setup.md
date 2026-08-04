# Headroom + DeepSeek Direct — Setup Reference (2026-06-18)

## The problem
Headroom proxy default `/v1/chat/completions` → `api.openai.com` (hardcoded). OpenRouter/DeepSeek calls were misrouted.

## The fix — env var override
```powershell
$env:OPENAI_TARGET_API_URL = "https://api.deepseek.com"
& "C:/Users/khoans/AppData/Local/Python/pythoncore-3.14-64/Scripts/headroom.exe" proxy --port 8787 --openai-api-url https://api.deepseek.com
```

After this, routing shows:
- `/v1/chat/completions` → `https://api.deepseek.com` ✅
- `/v1/responses` → `https://api.deepseek.com` ✅

## Previously (OpenRouter backend — deprecated for this setup)
```powershell
& "C:/Users/khoans/AppData/Local/Python/pythoncore-3.14-64/Scripts/headroom.exe" proxy --port 8787 --backend openrouter
```

## Env var vs flag

| Method | Command | Persists |
|--------|---------|----------|
| **Flag** | `--openai-api-url https://api.deepseek.com` | This session only |
| **Env var** | `$env:OPENAI_TARGET_API_URL="..."` | Only while terminal open |

## API key
DeepSeek API key is NOT set in Headroom. Hermes sends it via Authorization header in each request. The proxy passes it through transparently.

## Verification
```bash
curl http://127.0.0.1:8787/stats | python -c "import sys,json; d=json.load(sys.stdin); print('Requests:', d.get('proxy_inbound',{}).get('total',0))"
```

## Profiles configured (both)
- `lusine-profile`: `headroom.enabled: true`, `model.base_url: http://127.0.0.1:8787`
- `personal_profile`: same

## Caveat
Headroom does NOT auto-load `.env` files. The var name in .env must be `OPENAI_TARGET_API_URL`, not `HEADROOM_OPENAI_API_URL` (wrong learing from earlier).