# Mem0 Troubleshooting — 4-Layer Diagnostic Pattern

When Hermes reports `Mem0 backend not initialized` or `No module named 'mem0'`, diagnose in this order.

## Layer 1: Config — Is mem0 configured?

Check `config.yaml` under the profile:

```yaml
memory:
  provider: mem0    # ← must be 'mem0'
  ...
```

But that alone is not enough. mem0 also needs its own config block. Look for a top-level `mem0:` key:

```yaml
mem0:
  api_key: ''       # optional for local Qdrant; required for cloud
  base_url: ''      # if using mem0 cloud
  qdrant_url: ''    # if using self-hosted Qdrant
```

**Common pitfall:** `provider: mem0` is set but the `mem0:` config block is entirely absent → Hermes tries to init mem0 with zero params → fails silently.

**Check via terminal:**
```bash
grep -A5 "^memory:" ~/AppData/Local/hermes/profiles/<profile>/config.yaml
grep -A5 "^mem0:" ~/AppData/Local/hermes/profiles/<profile>/config.yaml
```

## Layer 2: Package — Is mem0 installed?

```
pip show mem0       → not found  → need `pip install mem0`
pip show qdrant-client  → not found  → need `pip install qdrant-client`
python -c "import mem0"  → ModuleNotFoundError
```

**On Windows Hermes environments** (git-bash, multiple Pythons):
- Check `which python` / `python -c "import sys; print(sys.executable)"` to confirm you're in the right venv
- Hermes Desktop typically runs under its bundled Python, not the system python
- Use `hermes setup` or check `config.yaml` for the target python path

## Layer 3: Docker — Is Qdrant running?

Local mem0 typically uses a Qdrant vector DB, often via Docker:

```bash
docker ps | grep qdrant    # check running containers
docker ps -a | grep qdrant  # check if stopped
```

If Docker daemon doesn't respond:

```
failed to connect to the docker API at npipe:////./pipe/dockerDesktopLinuxEngine
```

→ **Docker Desktop is not running** on the machine. Qdrant cannot start.

## Layer 4: Qdrant Server — Is port 6333 reachable?

Even if Docker runs, verify Qdrant is actually listening:

```bash
# Windows
netstat -an | grep 6333
# or
curl -s http://localhost:6333/health 2>&1
```

If nothing listens on 6333 → Qdrant never started. Common causes:
- Docker container exited (check `docker ps -a`)
- Port conflict (another service on 6333)
- Qdrant crashed on startup (check `docker logs <qdrant-container>`)

## Recovery Playbook

### Option A: Local Qdrant via Docker
```bash
# Start Docker Desktop first, then:
docker run -d --name qdrant -p 6333:6333 qdrant/qdrant
# Verify: curl http://localhost:6333/health
# Then pip install: pip install mem0 qdrant-client
```

### Option B: Cloud Qdrant (no Docker)
Get a free Qdrant cloud instance → copy the URL + API key → add to config.yaml:
```yaml
mem0:
  qdrant_url: https://xxxx-xxxx.us-east-0.aws.cloud.qdrant.io:6333
  api_key: your-api-key-here
```

### Option C: Fallback to Hermes built-in memory
If mem0 is too complex for the current environment, change `provider` to the Hermes built-in:

```yaml
memory:
  provider: file  # ← switches to MEMORY.md/USER.md only, no vector DB needed
```

## Verification

After fixing, verify:

```python
python -c "
from hermes_tools import mem0_search
try:
    results = mem0_search('test')
    print('mem0 OK:', results)
except Exception as e:
    print('mem0 FAIL:', e)
"
```

Or simply start a new session — the init error should be gone from Hermes startup.
