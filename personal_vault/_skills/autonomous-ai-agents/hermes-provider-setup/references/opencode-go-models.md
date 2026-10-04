# OpenCode GO — Model List (API Response)

**Retrieved from:** `GET https://opencode.ai/zen/go/v1/models`  
**Date:** 2026-06-26  
**Auth:** Bearer `sk-...` (Go subscription key)

## Full Model List

| # | Model ID | Owned By |
|---|----------|----------|
| 1 | `minimax-m3` | opencode |
| 2 | `minimax-m2.7` | opencode |
| 3 | `minimax-m2.5` | opencode |
| 4 | `kimi-k2.7-code` | opencode |
| 5 | `kimi-k2.6` | opencode |
| 6 | `kimi-k2.5` | opencode |
| 7 | `glm-5.2` | opencode |
| 8 | `glm-5.1` | opencode |
| 9 | `glm-5` | opencode |
| 10 | `deepseek-v4-pro` | opencode |
| 11 | `deepseek-v4-flash` | opencode |
| 12 | `qwen3.7-max` | opencode |
| 13 | `qwen3.7-plus` | opencode |
| 14 | `qwen3.6-plus` | opencode |
| 15 | `qwen3.5-plus` | opencode |
| 16 | `mimo-v2-pro` | opencode |
| 17 | `mimo-v2-omni` | opencode |
| 18 | `mimo-v2.5-pro` | opencode |
| 19 | `mimo-v2.5` | opencode |
| 20 | `hy3-preview` | opencode |

## Usage Notes

- **Model IDs are bare** — do NOT prefix with `opencode-go/` or `opencode/` when calling via Hermes provider
- Endpoint: `https://opencode.ai/zen/go/v1` (NOT `api.opencode.ai/v1`)
- OpenAI-compatible (`/v1/chat/completions`)
- List may change as OpenCode adds/removes models
