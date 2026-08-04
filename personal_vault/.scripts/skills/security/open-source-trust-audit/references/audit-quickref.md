# Trust Audit Quick Reference

## One-liner Network Check (full src/)
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

## One-liner Telemetry Check
```bash
for t in telemetry analytics segment mixpanel posthog sentry amplitude datadog newrelic; do
  grep -rn --include='*.py' -l "$t" src/ | head -3
done
```

## One-liner Subprocess Check
```bash
grep -rn --include='*.py' -l 'import subprocess\|os\.system\|os\.popen\|pty\.spawn' src/
```

## One-liner File Write Check
```bash
grep -rn --include='*.py' '\.write(\|atomic_write\|open(.*"w\|open(.*"a' src/
```

## Verdict Table Template
```
| Dimension               | Verdict                            |
|-------------------------|------------------------------------|
| Network/API calls       | ✅ NONE / ⚠️ CONTROLLED / ❌ FOUND |
| Telemetry/Analytics     | ✅ NONE / ❌ FOUND                  |
| Runtime dependencies    | ✅ ZERO / ⚠️ MINIMAL / ❌ HEAVY    |
| Subprocess safety       | ✅ NONE / ⚠️ CONTROLLED / ❌ DANGEROUS |
| File writes             | ✅ LOCAL ONLY / ❌ SYSTEM-WIDE      |
| MCP/Plugin transport    | ✅ STDIO ONLY / ❌ NETWORK LISTENER |
| Install script          | ✅ STANDARD / ❌ DANGEROUS          |
| CI/CD                   | ✅ STANDARD / ❌ SUSPICIOUS         |
```
