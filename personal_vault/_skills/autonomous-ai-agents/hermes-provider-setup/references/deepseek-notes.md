# DeepSeek Provider Notes

## API authentication

DeepSeek uses OpenAI-compatible API. Headroom forwards the auth header as-is.

API key is stored in Hermes `providers` config (not env var):

```yaml
providers:
  deepseek:
    api_key: "<sk-...>"
    base_url: http://127.0.0.1:8787
```

## Headroom routing quirk

The proxy startup banner always shows:

```
/v1/chat/completions    → https://api.openai.com
```

Even when `--openai-api-url https://api.deepseek.com` actually overrides it.
The override IS active — trust the flag, not the banner. Verified via successful LLM
responses and `/stats` showing non-zero `api_requests`.

## Model names

- Hermes config name for routing: provider-prefixed (`deepseek/deepseek-v4-flash`)
- DeepSeek native API name (if calling directly): `deepseek-chat` (V3), `deepseek-reasoner` (R1)

## Proxy toggle

Warren's toggle pattern: start proxy → DeepSeek mode; stop proxy → Nous free.
No profile switch needed. `model.base_url` stays at `http://127.0.0.1:8787` in both modes.

## API key safety

- Key was set via `hermes config set providers.deepseek.api_key "..."` — stored in config.yaml
- Key was NOT exposed in USER_GUIDE.md (redacted to `***`)
- Key was NOT committed to git (gitignore has `.env`)

## Pricing — DeepSeek V4 Peak/Valley (mid-July 2026)

DeepSeek introduced peak-valley pricing for V4 official launch. Regular price = same as current; peak price = ×2.

### deepseek-v4-flash

| Item | Regular | Peak (×2) |
|------|--------:|----------:|
| 1M input (cache hit) | $0.0028 | $0.0056 |
| 1M input (cache miss) | $0.14 | $0.28 |
| 1M output | $0.28 | $0.56 |

### deepseek-v4-pro

| Item | Regular | Peak (×2) |
|------|--------:|----------:|
| 1M input (cache hit) | $0.003625 | $0.00725 |
| 1M input (cache miss) | $0.435 | $0.87 |
| 1M output | $0.87 | $1.74 |

### Peak hours (UTC → Vietnam UTC+7)

| UTC | Vietnam | |
|:---|:---|---:|
| 1:00–4:00 AM | **8:00–11:00 AM** | Sáng ☀️ |
| 6:00–10:00 AM | **1:00–5:00 PM** | Chiều ☀️ |

→ **Hầu hết giờ làm việc (8AM-5PM) đều peak.**

### Impact on Warren

Xài qua **OpenCode Zen** (pass-through pricing nên peak cũng pass-through).
Cách tránh: xài off-peak (trước 8AM hoặc sau 5PM), hoặc chuyển provider.

## Cheaper alternatives to DeepSeek direct

### deepseek-v4-flash qua OpenRouter (Wafer provider)

Cheapest option — **$0.09/M input, $0.18/M output** (36% rẻ hơn DeepSeek regular).

| Provider | Input /M | Output /M | Uptime |
|----------|---------:|----------:|:------:|
| **Wafer** (OpenRouter) | **$0.09** | **$0.18** | 93% |
| GMICloud (OpenRouter) | $0.098 | $0.196 | 99.5% |
| DeepInfra (OpenRouter) | $0.10 | $0.20 | 97.7% |
| Alibaba Cloud Int. (OpenRouter) | $0.134 | $0.268 | 99.8% |
| DeepSeek direct / OpenCode Zen | $0.14 | $0.28 | 99.9% |

OpenRouter auto-failover: nếu Wafer chậm/down, route sang provider khác tự động.

### Cách setup OpenRouter cho deepseek-v4-flash

```bash
# Hermes đã có OpenRouter key — chỉ cần switch
hermes config set model.provider openrouter
hermes config set model.default "deepseek/deepseek-v4-flash"
# Restart session (/reset hoặc F5)
```

### Other model alternatives

| Model | Provider | Input /M | Output /M | Ghi chú |
|-------|----------|---------:|----------:|:--------|
| MiniMax M3 | OpenCode Zen | $0.30 | $1.20 | Output đắt hơn |
| GLM-4.5-Air | Z.ai direct | $0.20 | $1.10 | Built-in Hermes provider (#17 Z.AI/GLM) |
| GLM-4.5-Air | OpenRouter | $0.13 | $0.50 | |
| MiMo-V2.5 | OpenCode Zen | $0.14 | $0.28 | Ngang giá DeepSeek |

### OpenCode Go subscription

$10/tháng — includes deepseek-v4-flash (31,650 requests/5h limit).
Nếu usage thấp → đắt hơn pay-per-token. Nếu usage cao → tiết kiệm.
