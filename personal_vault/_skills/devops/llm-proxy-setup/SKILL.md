---
name: llm-proxy-setup
description: "Install, configure, and wire local LLM proxy backends (Headroom, etc.) into Hermes profiles. Covers env vars, port management, profile config, and PowerShell launch patterns."
version: 1.0
trigger: when setting up a local LLM proxy, changing provider backends, or needing compression/token savings on specific profiles
---

# Local LLM Proxy Setup

Use this when wiring a local proxy (e.g. Headroom) into Hermes to compress context, save tokens, or route through a specific API backend.

---

## General Workflow

### 1. Install proxy tool
```bash
pip install headroom-ai[all]  # or specific proxy tool
```
On Windows with Python 3.14+, Rust MSVC toolchain may be required for native builds (see `windows-toolchain-install-verification` skill).

### 2. Start proxy with correct backend
```powershell
& "path/to/proxy.exe" proxy --port 8787 [--backend/--flags]
```

| Backend | Flag | Env var for endpoint override |
|---------|------|-------------------------------|
| OpenAI-compatible (DeepSeek, OpenRouter, etc.) | `--openai-api-url https://api.deepseek.com` | `OPENAI_TARGET_API_URL` |
| OpenRouter | `--backend openrouter` | — |
| Anthropic | Default | `ANTHROPIC_TARGET_API_URL` |

### 3. Configure Hermes profiles
```bash
hermes config set model.base_url "http://127.0.0.1:8787" --profile <name>
hermes config set headroom.enabled true --profile <name>
hermes config set headroom.port 8787 --profile <name>
```

### 4. Restart Hermes Desktop
Proxy 1 instance duy nhất — tất cả profile có `model.base_url: http://127.0.0.1:8787` đều dùng chung.

---

## Windows Shell Pitfalls

| Issue | Fix |
|-------|-----|
| `& "C:/..." proxy --port 8787` → `AmpersandNotAllowed` in full command line | Use `& 'C:/path/...'` (single quotes and only `&` at start). Or cd first: `cd scripts; ./headroom.exe proxy` |
| `taskkill //F //PID N` syntax error in git-bash | Use `taskkill -F -PID N` (dash flags, not slash flags) |
| Python scripts not on PATH | Use full path: `C:/Users/khoans/AppData/Local/Python/pythoncore-3.14-64/Scripts/headroom.exe` |
| `.env` not auto-loaded by Headroom | Must set env vars explicitly before proxy start, or use `--flag` |
| Port already in use (Errno 10048) | Kill old process first: `taskkill -F -PID <pid>` |

---

## Proxy Routing Verification

After starting proxy, check:
```bash
curl http://127.0.0.1:8787/stats
# proxy_inbound.total should increment after each request
```

The startup banner shows routing table — verify `/v1/chat/completions` points to your intended backend, not default `api.openai.com`.

---

## Documenting for Non-IT Users

When this setup is complete:
- Update `vault/USER_GUIDE.md` with simplified Vietnamese copy-paste instructions
- Format: table showing when to enable/disable + PowerShell command to copy
- Save guide path in memory so next session knows where the source of truth lives

---

## References

| File | Purpose |
|------|---------|
| `references/hermes-headroom-deepseek-setup.md` | Session-specific: Headroom v0.24.0 + DeepSeek direct API setup with env vars and routing fix |