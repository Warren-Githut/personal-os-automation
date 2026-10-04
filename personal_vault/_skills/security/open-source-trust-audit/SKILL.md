---
name: open-source-trust-audit
description: Trust audit for third-party Python source before adoption.
---

# Open Source Trust Audit

## When to Use

- Evaluating whether a third-party Python project is safe to install or use
- Performing due diligence on a dependency before adoption
- Verifying that a project's stated security boundaries match its actual code
- Answering: "Does this project phone home, steal data, or expose risk I didn't sign up for?"

## Overview

A trust audit is a **due-diligence check** — not a full penetration test. The methodology is systematic: grep the source for specific patterns, read the build/packaging metadata, check sidecar files and CI, then render a verdict.

## Audit Phases

### Phase 1: Surface Metadata

- **`pyproject.toml`**: Check `dependencies = []` vs actual imports. Zero runtime deps is the cleanest signal.
- **`[project.scripts]`**: What CLI entry points are registered?
- **`SECURITY.md` / `CODE_OF_CONDUCT.md` / `LICENSE`**: Governance and stated security boundaries.
- **`CLAUDE.md` / `README.md`**: What does the project claim about itself? Verify those claims against the code.

### Phase 2: Network Call Detection

Search for any HTTP/network client import:

```bash
grep -rn --include='*.py' \
  -e 'import requests\|from requests' \
  -e 'import urllib\|from urllib' \
  -e 'import httpx\|from httpx' \
  -e 'import aiohttp\|from aiohttp' \
  -e 'import socket\|from socket' \
  -e 'import http\.client\|from http\.client' \
  -e 'urlopen' src/
```

Also check for AI/provider SDK imports and transport layers:

```bash
grep -rn --include='*.py' \
  -e 'import.*openai\|from.*openai' \
  -e 'import.*anthropic\|from.*anthropic' \
  -e 'import.*boto3\|from.*boto3' \
  -e 'import.*grpc\|from.*grpc' \
  -e 'import.*websocket\|from.*websocket' \
  src/
```

**Interpretation**: `urllib.parse` = URL parsing only (safe). Everything else = actual network I/O (investigate).

### Phase 3: Telemetry / Analytics Detection

```bash
for term in telemetry analytics segment mixpanel posthog sentry amplitude datadog newrelic google_analytics countly; do
  grep -rn --include='*.py' -l "$term" src/ | head -5
done
```

**Critical check**: Are matches in **catalog/definition text** (safe — the project describes other tools/concepts) or actual **SDK imports** (red flag)?

### Phase 4: Subprocess Spawn Analysis

```bash
grep -rn --include='*.py' -l 'import subprocess\|from subprocess\|os\.system\|os\.popen\|pty\.spawn' src/
```

**Safety ruler (worst → best):**

| Pattern | Verdict |
|---------|---------|
| `shell=True` with user-influenced args | **REJECT** |
| `shell=False` with uncontrolled args | **CAUTION** |
| `shell=False` with allowlisted templates | **ACCEPTABLE** |
| `subprocess.run()` + allowlist + shell metachar rejection + bounded timeouts | **SAFE** |
| No subprocess at all | **BEST** |

For each subprocess call, check: Is `shell=False` used? Is the command allowlisted? Are args bounded? Is there a claim boundary documented?

### Phase 5: File Write Analysis

```bash
grep -rn --include='*.py' '\.write(\|\.writelines\|atomic_write\|open(.*"w\|open(.*"a' src/
grep -rn --include='*.py' '\.write_text(' src/
```

- **Safe**: writes bounded to `~/.<project>/` or project-local paths; uses atomic writes (temp + rename)
- **Red flag**: writes to system paths (`/etc/`, `/usr/`, `C:\Windows\`), user config without permission, or `/tmp` without cleaning up

### Phase 6: MCP / Plugin / Extension Analysis

```bash
# MCP server detection
grep -rn --include='*.py' 'mcp\|ModelContextProtocol' src/

# Plugin detection
ls -la src/plugin_bundle*/ **/plugin.yaml **/plugin.json 2>/dev/null
```

**Transport safety**:
| Transport | Risk |
|-----------|------|
| stdio (stdin/stdout) | **Safe** — no open port, no remote access |
| TCP/HTTP listener | **CAUTION** — opens a network port; check auth/access controls |
| Unix socket | **NEUTRAL** — local-only; verify permissions |

Check what tools/resources the MCP server exposes. Metadata-only tools (status, probe, recommend) are safer than arbitrary shell-access tools.

### Phase 7: Install Script Review

If the project ships `install.sh` or similar:

- Does it download from a controllable URL? (preview/stable channel selection is normal)
- Does it create an isolated venv or install system-wide?
- Does it require `sudo`?
- Does it modify system configuration?
- Does it have pre/post-install hooks that run silently?
- Are pip args controllable via environment variables? (advanced hatch, but audit it)

### Phase 8: CI/CD Review

```bash
ls .github/workflows/ 2>/dev/null
```

- **Normal**: test → lint → build → deploy to GitHub Pages
- **Suspicious**: uploading credentials, curl-to-bash from unknown hosts, `pull_request_target` with write permissions, decrypting untracked files
- **Supply-chain risk**: CI that runs `pull_request_target` can expose repo secrets to PRs from forks

### Phase 9: Dependency Footprint

Zero declared deps (`dependencies = []`) = best signal. Each declared dep is a transitive supply-chain surface. Check:

- `requirements*.txt`, `Pipfile*`, `poetry.lock`, `uv.lock`
- Group/lint deps separate from runtime deps
- Build-only deps (setuptools, hatchling) don't count as runtime risk

### Phase 10: Verdict

Summarize findings with a structured verdict table:

| Dimension | Verdict | Notes |
|-----------|---------|-------|
| Network/API calls | ✅ NONE / ⚠️ CONTROLLED / ❌ FOUND | |
| Telemetry/Analytics | ✅ NONE / ❌ FOUND | |
| Runtime dependencies | ✅ ZERO / ⚠️ MINIMAL / ❌ HEAVY | |
| Subprocess safety | ✅ NONE / ⚠️ CONTROLLED / ❌ DANGEROUS | |
| File writes | ✅ LOCAL ONLY / ❌ SYSTEM-WIDE | |
| MCP/Plugin safety | ✅ STDIO ONLY / ❌ NETWORK LISTENER | |
| Install script | ✅ STANDARD / ❌ DANGEROUS | |
| CI/CD | ✅ STANDARD / ❌ SUSPICIOUS | |

**Verdict enum:**
- **USE** — no concerning signals; code matches stated boundaries
- **USE WITH CAUTION** — minor concerns documented; pin a specific version
- **DO NOT USE** — phones home, steals data, modifies system, has malicious behavior

## Claim Boundaries

- This is a point-in-time static analysis, not a full penetration test
- It does not catch all supply-chain risks (sub-dependency compromise)
- Absence of evidence ≠ evidence of absence — a clean grep is a strong signal, not a guarantee
- Compiled extensions (`.so`, `.pyd`) are opaque to text-based grep; build-time hooks (setup.py) can run code not visible in src/

## Pitfalls

- **False positives**: "telemetry" in a skill description ≠ telemetry SDK import. Always check file context.
- **False negatives**: Dynamic imports / `__import__()` / `exec()` / `eval()` can hide network calls from static grep
- **Compiled binaries**: Native extensions are invisible to text search
- **Build-time hooks**: `setup.py` pre/post install scripts can run arbitrary code not in `src/`
- **Sub-dependencies**: A clean top-level package can transitively depend on a compromised library
- **Version drift**: Trustworthiness is per-version; a release that passes audit today may not tomorrow
