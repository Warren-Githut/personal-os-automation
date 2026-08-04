# xAI / Grok Provider Setup — Session Notes

## Quick Reference

| Item | Value |
|------|-------|
| Provider name in Hermes | `xai` |
| Env var | `XAI_API_KEY` |
| Console (get API key) | https://console.x.ai |
| Consumer plans (NOT API) | grok.com (SuperGrok Lite $10, SuperGrok $30, Heavy $300) |
| Free API credits | ⚠️ NONE. New accounts = 0 credits. Must add payment at console.x.ai/team/.../billing. Blog claims of "$150/mo free credits" are [LOW] and wrong — verified via curl test (2026-06-24). |
| Cheapest model | `grok-4.1-fast` — $0.20/M in, $0.50/M out, 2M ctx |
| Flagship model | `grok-4.3` — $1.25/M in, $2.50/M out, 1M ctx |

## Setup Commands (Verified 2026-06-24)

```bash
# 1. Set API key in Hermes config (works — direct config patch is blocked)
hermes config set providers.xai.api_key "xai-..."

# 2. (Optional) Add to .env for fallback
grep -q "XAI_API_KEY" "$HERMES_HOME/.env" || echo 'XAI_API_KEY=xai-...' >> "$HERMES_HOME/.env"

# 3. Switch model to xAI
hermes config set model.provider xai
hermes config set model.default grok-4.1-fast
# Or use interactive picker: hermes model

# 4. New session required
/reset
```

## Consumer Subscription Trap

SuperGrok Lite ($10/mo) and other grok.com plans are **web/app subscriptions only**. They do NOT include API credits or API keys. The user asked about buying SuperGrok Lite — correct answer was "skip it, grab an API key from console.x.ai instead." (Note: new accounts have zero credits — must add payment at console.x.ai to use API.)

The `hermes config set` method worked correctly. Attempting `patch` on `config.yaml` was refused with:
```
Refusing to write to Hermes config file: ...
Agent cannot modify security-sensitive configuration.
Edit ~/.hermes/config.yaml directly or use 'hermes config' instead.
```

## API Key Verification (MANDATORY before declaring setup complete)

Always test the key + credit balance with curl:

```bash
curl -s https://api.x.ai/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer *** \
  -d '{"model":"grok-4.3","messages":[{"role":"user","content":"Say hi in 3 words"}],"max_tokens":20}'
```

### Error interpretation

| Response | Meaning | Action |
|----------|---------|--------|
| `{"code":"permission-denied","error":"...no credits..."}` | Key valid, account has 0 credits | Must add payment at https://console.x.ai |
| `401 Unauthorized` | Invalid/expired key | Regenerate key at console.x.ai |
| Valid response with `choices[0].message.content` | Ready to use | Proceed with model switch |

**Verified scenario (2026-06-24):** New xAI account with valid API key → `permission-denied` + "no credits or licenses". The $150/mo free credits claim from mem0.ai and felloai blogs is [LOW] — do not repeat without official xAI source.

On this Windows system (stock-profile):
- HERMES_HOME = `C:\Users\khoans\AppData\Local\hermes\profiles\stock-profile`
- Config: `$HERMES_HOME/config.yaml` (13KB)
- .env: `$HERMES_HOME/.env` (24KB, already existed)
- The `~/.hermes/` symlink also points here but `read_file` resolvers may not follow it correctly
