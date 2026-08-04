---
name: memory-provider-setup
description: Configure and troubleshoot Hermes memory providers (mem0 OSS, mem0 Platform, Honcho, etc.). Covers local FAISS (in-process) + Ollama stack, dimension matching, config file location, and activation.
version: 1.10.0
author: Hermes (learned from Warren's mem0 setup + debugging sessions 2026-06-24, 2026-06-25, 2026-06-27)
created: 2026-06-24
tags: [hermes, memory, mem0, faiss, ollama, windows]
related_skills: [hermes-provider-setup, debugging-and-error-recovery]
---

# Memory Provider Setup

## Overview

Hermes supports pluggable memory providers. The `memory.provider` config key in `config.yaml` selects the active provider:

| Provider | Mode | Backend |
|----------|------|---------|
| `builtin` | Hermes native | Flat key-value, 2,200 char limit, shown in system prompt |
| `mem0` | Platform (cloud) | Mem0 Platform API — needs API key |
| `mem0` | OSS (self-hosted) | Local Qdrant + LLM + embedder — **no API key needed when using Ollama for all components** |

**Config file is NOT config.yaml.** Hermes mem0 plugin reads from `$HERMES_HOME/mem0.json`. The `mem0:` block in config.yaml is IGNORED by the plugin (it's for platform-mode fallback only).

---

## mem0 OSS Mode Setup (Local, No API Key)

### Requirements

| Component | Option | Notes |
|-----------|--------|-------|
| Vector DB | Qdrant (Docker or Embedded) | Docker: `docker run -d --name qdrant -p 6333:6333 qdrant/qdrant`; Embedded: `pip install qdrant-client` with file path config |
| LLM | Ollama | `ollama pull llama3.2:3b` (or any supported model) |
| Embedder | Ollama | `ollama pull nomic-embed-text` (768 dims, free, local) |
| Python | mem0ai | `pip install mem0ai qdrant-client ollama` |

### Step-by-Step

#### 1. Start Qdrant

**Option A — Docker (HTTP mode):**
```bash
# Check Docker is running
docker ps

# Start Qdrant
docker run -d --name qdrant -p 6333:6333 --restart unless-stopped qdrant/qdrant

# Verify
curl -s http://localhost:6333/healthz
# → "healthz check passed"
```

**Option B — Embedded (path mode, no Docker):**
No service to start. Embedded Qdrant runs in-process via `qdrant-client` Python library.
Just create the target directory:
```bash
mkdir -p ~/.hermes/qdrant/<profile-name>
```
The Qdrant driver initializes the collection on the first mem0 write — no separate service needed.

#### 2. Install Python packages

```bash
pip install mem0ai qdrant-client ollama
```

**IMPORTANT:** PyPI package name is `mem0ai`, NOT `mem0`. `pip install mem0` will fail.

#### 3. Ensure Ollama is running with required models

```bash
ollama pull llama3.2:3b
ollama pull nomic-embed-text
ollama serve  # if not already running
```

#### 4. Create `mem0.json` in profile directory

Path: `$HERMES_HOME/mem0.json` (e.g. `C:\Users\khoans\AppData\Local\hermes\profiles\stock-profile\mem0.json`)

```json
{
  "vector_store": {
    "provider": "qdrant",
    "config": { "url": "http://localhost:6333", "embedding_model_dims": 768 }
  },
  "llm": {
    "provider": "ollama",
    "config": { "model": "llama3.2:3b", "ollama_base_url": "http://localhost:11434" }
  },
  "embedder": {
    "provider": "ollama",
    "config": { "model": "nomic-embed-text", "ollama_base_url": "http://localhost:11434", "embedding_dims": 768 }
  }
}
```
> NOTE: This is the **flat schema** for mem0 2.0.10. The old `"mode": "oss"` + `"oss": {...}` wrapper is INVALID in 2.0.10 (silently ignored → OpenAI fallback error). See "CRITICAL: mem0 2.0.10 config is FLAT" above.

#### 5. Activate

Start a **new Hermes session**. Mem0 plugin is only activated on session start.

---

### Embedded Qdrant (No Docker)

For truly local setups with zero Docker dependency, use embedded (in-process) Qdrant. The `qdrant-client` Python library can run Qdrant embedded in the same process, writing directly to disk.

**Advantages over Docker Qdrant:**
- No Docker Desktop needed
- No Docker startup/downtime dependency
- Faster init (no network call)
- Truly local — works offline

**Tradeoffs:**
- No REST API access (can't browse with HTTP tools)
- Tied to the Python process lifecycle
- Slightly different perf characteristics for large collections

**mem0.json config (embedded):**
**mem0.json config (embedded, flat schema for 2.0.10):**
```json
{
  "vector_store": {
    "provider": "qdrant",
    "config": {
      "path": "C:/Users/khoans/.hermes/qdrant/<profile-name>",
      "embedding_model_dims": 768,
      "on_disk": true
    }
  },
  "llm": {
    "provider": "ollama",
    "config": { "model": "llama3.2:3b", "ollama_base_url": "http://localhost:11434", "temperature": 0.2, "max_tokens": 2000 }
  },
  "embedder": {
    "provider": "ollama",
    "config": { "model": "nomic-embed-text", "ollama_base_url": "http://localhost:11434", "embedding_dims": 768 }
  }
}
```
> Flat schema (NO `oss` wrapper) — required for mem0 2.0.10. See "CRITICAL: mem0 2.0.10 config is FLAT" above.

Note: `temperature` and `max_tokens` in the LLM config are optional but recommended for consistent behavior across writes.

Key differences from Docker config:
- `path` instead of `url` — points to a local directory
- `on_disk: true` — stores vectors on disk (not in-memory)
- No Docker container needed

---

## Multi-Profile Architecture

Hermes stores mem0 config **per profile**, not globally. Each profile has its own:

- `$HERMES_HOME/profiles/<profile>/config.yaml` — must have `memory.provider: mem0`
- `$HERMES_HOME/profiles/<profile>/mem0.json` — the actual mem0 OSS config
- `$HERMES_HOME/profiles/<profile>/skills/` — may be a symlink to another profile's skills

Key locations:
```
# App-level (global)
~/AppData/Local/hermes/config.yaml
~/AppData/Local/hermes/memories/

# Per-profile  
~/AppData/Local/hermes/profiles/<profile>/config.yaml
~/AppData/Local/hermes/profiles/<profile>/mem0.json
```

NOTE: `~/.hermes/` and `~/AppData/Local/hermes/` are SEPARATE directory trees. The Hermes app uses `~/AppData/Local/hermes/`. The `~/.hermes/` directory may exist for other tooling but is NOT the source of truth for app config.

### Cross-Profile Diagnostic

To check which profiles have mem0 and their config:

```bash
for p in profiles/*/; do
  name=$(basename "$p")
  echo "=== $name ==="
  grep "provider: mem0" "$p/config.yaml" 2>/dev/null && echo "  ✅ memory.provider=mem0" || echo "  ❌ no mem0 provider"
  ls "$p/mem0.json" 2>/dev/null && echo "  ✅ mem0.json exists" || echo "  ❌ no mem0.json"
  python3 -c "import json; c=json.load(open('$p/mem0.json')); print(f'  user_id={c.get(\"user_id\")}, vector_store={c[\"oss\"][\"vector_store\"][\"provider\"]}')" 2>/dev/null || echo "  (unparseable)"
done
```

### Adding mem0 to a new profile

Three things needed:
1. **config.yaml** — set `memory.provider: mem0` in the profile's config
2. **mem0.json** — create with OSS config pointing to Qdrant (shared or per-profile)
3. **Packages** — `pip install mem0ai qdrant-client ollama` (once, global venv)

### Embedded vs Docker per profile

| Profile | Backend | user_id | Status |
|---------|---------|---------|--------|
| stock-profile | Embedded (path) | `warren_stock` | ✅ active |
| warren-profile | Embedded (path) | `warren` | ✅ active |
| personal_profile | Embedded (path) | `warren_personal` | ✅ active |
| lusine-profile | (none) | — | ❌ needs setup |

Different `user_id` values = isolated mem0 data per profile. This is by design — each profile has its own memory space.

See `references/three-profile-consistent-setup-2026-06-25.md` for the exact configs used in Warren's setup.

---

## Critical: Embedding Dimension Matching

**This is the #1 source of failure.** The embedder dimension must match the Qdrant collection dimension. If they mismatch, mem0 will fail with:

```
qdrant_client.http.exceptions.UnexpectedResponse: Unexpected Response: 400 (Bad Request)
Raw response content:
b'{"status":{"error":"Wrong input: Vector dimension error: expected dim: 1536, got 768"}}'
```

**Fix:** Set `embedding_model_dims` in `vector_store.config` to match what the embedder produces:

| Embedder Model | Dims | Config Value |
|---------------|------|-------------|
| nomic-embed-text | 768 | `embedding_model_dims: 768` |
| text-embedding-3-small | 1536 | `embedding_model_dims: 1536` |
| text-embedding-3-large | 3072 | `embedding_model_dims: 3072` |

If Qdrant already has a collection with wrong dims, delete it and let mem0 recreate:

```python
from qdrant_client import QdrantClient
c = QdrantClient(url='http://localhost:6333')
for col in c.get_collections().collections:
    c.delete_collection(col.name)
```

---

## mem0 Platform Mode Setup (Cloud API)

### Config via interactive wizard

```bash
hermes memory setup
```

Or non-interactive:

```bash
hermes memory setup --mode platform --api-key "m0-xxxx"
```

### Config file structure

API key goes in `.env` as `MEM0_API_KEY`.
Non-secret config goes in `mem0.json`:

```json
{
  "mode": "platform",
  "user_id": "warren_stock",
  "agent_id": "hermes",
  "rerank": true
}
```

---

## Hermes Desktop "Memory Provider Panel" — it's HINDSIGHT, not mem0/Obsidian (2026-07-19)

**Warren misconception:** He saw a "Memory Provider Panel — Clean UI for memory configuration (local, Obsidian, Mem0, etc.)" and asked if it applies to him, assuming it covers Obsidian/mem0. **It does NOT.** Verified against source on his machine (Hermes v0.18.2, upstream 36f2a966).

### What it actually is
- Location: Hermes Desktop → **Settings → Memory & Context**.
- Architecture: generic declarative renderer. Each provider declares its config surface in `hermes_cli/memory_providers.py` (`MemoryProvider` class, registry `MEMORY_PROVIDERS`). The desktop draws whatever fields a provider declares — zero bespoke UI per provider.
- **Only `hindsight` declares fields** → it's the ONLY provider with a visible config form (Mode / API key / API URL / Bank ID / Recall budget). All others (builtin, mem0, honcho) have **NO entry** in `MEMORY_PROVIDERS` → render **nothing**.
- So the panel Warren saw = **Hindsight** config form. Obsidian = Warren's vault notes (separate, NOT a Hermes memory provider). His actual mem0/FAISS setup has **NO panel**.

### Hindsight modes (from source)
| Mode | Behavior | Cost | Privacy |
|------|----------|------|---------|
| `cloud` (default) | Memory → Vectorize Hindsight Cloud API; only needs API key (free tier exists) | Free tier / paid | ❌ Data leaves machine |
| `local_external` | Point API URL at self-hosted Hindsight instance (Docker) | Free but +RAM/server | ✅ Local |

### Recommendation for Warren (Bố) — KEEP mem0/FAISS, do NOT switch
- Current memory = mem0/OSS **FAISS** (in-process, free, private, 24/7, laptop-only) — optimal per his constraints (see "Lightweight vector backend decision matrix" above).
- Switching via the panel would: (a) break FAISS, (b) push L'Usine ops data to a 3rd-party cloud, or (c) require self-hosting Docker (violates min-RAM/24-7 laptop constraint).
- **Agent rule:** If Warren mentions "the memory panel" / "memory settings UI" → explain it's Hindsight, confirm his mem0/FAISS is separate + healthy, advise NOT to click Save unless he wants cloud memory. Offer OneDrive-sync of `mem0_faiss/` for cross-device instead.
- Verify the panel ships in current version: `hermes --version` (Bố = v0.18.2 — present via commits `822c8226d`, `03d9a95a7`).

### Verify a Hermes UI feature against source (don't trust the label)
When Warren describes a UI element, verify on disk before answering:
1. `hermes --version` + `hermes config path` → install dir (`~/AppData/Local/hermes/hermes-agent`).
2. `cd` into it; `git log --oneline --all | grep -i "<feature>"` to confirm it ships in this version.
3. `grep -rli "<keyword>" hermes_cli agent tools` (NARROW dirs — full-tree grep TIMES OUT on large repos).
4. Read the declared schema file for exact fields.
> ⚠️ `search_files` tool FAILS on `~/AppData/Local/hermes/hermes-agent` (MSYS path conversion → IO error os 2). Use `terminal` `grep -rli` in narrowed subdirs instead.

See `references/hermes-desktop-memory-panel-hindsight.md` for the exact `memory_providers.py` HINDSIGHT declaration + commit list.

## Known Pitfalls

### Verify installed providers BEFORE recommending a swap (2026-07-08 lesson)

Web docs / GitHub READMEs list many mem0 vector backends (LanceDB, Tencent, etc.). **Do NOT trust them — verify what the installed mem0 version actually ships.** Warren's hermes venv pins `mem0 2.0.10`, which has `faiss.py` + `chroma.py` + `qdrant.py` but **NO `lancedb.py`** (LanceDB provider was not in 2.0.10 — `from mem0.vector_stores import LanceDB` raises `ImportError`). A swap plan built on LanceDB would have required a mem0 upgrade (risk breaking Hermes core) — caught only by listing the dir:

```bash
ls "$HERMES_VENV/Lib/site-packages/mem0/vector_stores/"
# → azure_ai_search.py chroma.py faiss.py qdrant.py ... (NO lancedb.py)
```

**Rule:** Before any "swap vector backend" proposal, `ls` the `vector_stores/` dir. Recommend only what is present (or a pip-installable extra that exists for that version). Upgrading mem0 to chase a missing provider is a LAST resort, not a default.

### Swap Qdrant → FAISS (in-process, no server) — VERIFIED 2026-07-08

**Why:** Warren runs on laptop-only, wants minimal RAM, zero cost, 24/7 uptime. Qdrant server (Docker or native) is the heaviest component. FAISS runs in-process (no server), ~50MB, free (keeps Ollama embedder). mem0 2.0.10 ships `faiss.py` natively — **no mem0 upgrade needed**.

**Config change** (`$HERMES_HOME/profiles/<profile>/mem0.json`):
```json
"vector_store": {
  "provider": "faiss",
  "config": {
    "path": "C:/Users/khoans/AppData/Local/hermes/profiles/<profile>/mem0_faiss",
    "embedding_model_dims": 768
  }
}
```
- Drop `url` (FAISS is path-based, not HTTP).
- `path` = local dir; mem0 creates `<collection>.faiss` + `<collection>.json` there.
- Keep `llm` + `embedder` (Ollama) unchanged → cost stays zero.
- Index type: `IndexFlatIP` (cosine) — mem0 default, fine for hundreds of vectors.

**Steps:**
1. Backup `mem0.json` → `mem0.json.bak`.
2. `pip install faiss-cpu` into the hermes venv (CPU build — laptop has no CUDA).
3. Edit `mem0.json` (provider + path, drop url).
4. Stop + kill Qdrant process (Docker: `docker stop qdrant`; native: `taskkill //F //IM qdrant.exe` via powershell). Keep the image for rollback.
5. Restart Hermes gateway so the mem0 plugin re-inits with FAISS.
6. Verify: `mem0_add(content="faiss swap test")` → `mem0_search(query="faiss swap")` returns it.
7. Verify cron `mem0-cleanup-warren` (CN 09:00) + `mem0-30day-review` still run — they call the mem0 API, FAISS is transparent.
8. Compare RAM before/after (`tasklist` / Resource Monitor) — expect Qdrant (~400MB) gone.

**Rollback:** restore `mem0.json.bak`, restart Qdrant, restart gateway.

**Cron dependency note:** `mem0-cleanup-warren` and `mem0-30day-review` depend on the **mem0 API**, not on Qdrant directly. Swapping the backend does NOT break them. (Verified: they use `mem0_*` tools, which route through the plugin regardless of backend.)

### Swap Qdrant → Chroma (embedded) — alternative

mem0 2.0.10 also ships `chroma.py`. Chroma embedded mode runs in-process (no server). Slightly heavier than FAISS (~100MB) but easier to configure and inspect. Use if FAISS has issues. Config: `"provider": "chroma"`, `"config": { "path": "<local_dir>", "embedding_model_dims": 768 }`.

### Lightweight vector backend decision matrix (Warren's constraints)

Warren's hard constraints: **laptop-only (min RAM), cost=0 (local), runs 24/7 (no fragile server)**. Evaluated options (deep-researched 2026-07-08 from tweets/repos):

| Option | Server? | RAM | Cost | Compat mem0 2.0.10 | Verdict |
|--------|---------|-----|------|---------------------|---------|
| Qdrant (current) | ✅ Docker/native | ~400MB | Free (Ollama) | native | ❌ too heavy |
| **FAISS** | ❌ in-process | ~50MB | Free | ✅ native | ✅ **OPTIMAL** |
| Chroma embedded | ❌ in-process | ~100MB | Free | ✅ native | 🟡 OK alt |
| LanceDB | ❌ embedded | ~80MB | Free | ❌ NOT in 2.0.10 | ❌ needs mem0 upgrade |
| Tencent Agent Memory | ✅ Node GW + API | ~150MB | 💸 API cost/extract | breaks mem0 | ❌ adds server + cost |
| zvec (Alibaba) | ❌ in-process lib | ~30-80MB | Free | ❌ no mem0 connector | ❌ build layer yourself |
| Gbrain (pgvector/MCP) | ✅ needs Postgres | heavy | Free | ❌ separate brain | ❌ overlaps mem0/WARREN_MEMORY |

**Conclusion:** FAISS is the optimal swap for Warren. Tencent/zvec/LanceDB/Gbrain were all researched and rejected: they are *memory/retrieval layers or engines*, not drop-in Qdrant replacements, and add servers/cost/complexity contrary to his constraints. See `references/lightweight-vector-backend-research-2026-07-08.md` for the full tweet/repo verdicts.

### CRITICAL: mem0 2.0.10 config is FLAT — NOT `oss` wrapper (2026-07-08)

ALL config examples above that use `"mode": "oss"` + `"oss": {...}` are **WRONG for mem0 2.0.10** (the version pinned in Warren's hermes venv). mem0 2.0.10 uses a **flat schema**: `vector_store` / `llm` / `embedder` at top level, NO `oss` wrapper, NO `mode` field.

**Symptom if you use the `oss` wrapper:** mem0 silently ignores the `oss` block → falls back to DEFAULT config → embedder defaults to **OpenAI** → `OpenAIError: The api_key client option must be set...` even though you configured Ollama. This is exactly what happened on 2026-07-08 — old `mem0.json` had `oss` wrapper, mem0 ignored it, tried OpenAI, failed.

**Correct flat config (mem0 2.0.10):**
```json
{
  "vector_store": {
    "provider": "faiss",
    "config": { "path": "<profile>/mem0_faiss", "embedding_model_dims": 768 }
  },
  "llm": {
    "provider": "ollama",
    "config": { "model": "llama3.2:3b", "ollama_base_url": "http://localhost:11434", "temperature": 0.2, "max_tokens": 2000 }
  },
  "embedder": {
    "provider": "ollama",
    "config": { "model": "nomic-embed-text", "ollama_base_url": "http://localhost:11434", "embedding_dims": 768 }
  }
}
```
- `MemoryConfig` (mem0 2.0.10) has NO `mode` field. `mode: "oss"` → AttributeError.
- Verify: `python -c "from mem0 import Memory; import json; Memory.from_config(json.load(open('mem0.json')))"` must init WITHOUT OpenAI error.

### Hermes 0.18.2 has NO `mem0_add` / `mem0_search` tools (2026-07-08)

The Hermes mem0 **plugin tools** (`mem0_add`, `mem0_search`, `mem0_list`, etc.) described elsewhere in this skill **do NOT exist** in Hermes 0.18.2's available toolset. Calling them returns `Tool 'mem0_add' does not exist.`

**Reality in 0.18.2:**
- mem0 is exposed via the **`memory` tool** (Hermes built-in memory) — which uses the FAISS backend configured in `mem0.json`. Use `memory(action='add'/'search')` for durable facts.
- For direct verification or bulk ops, call the **mem0 Python library directly**: `from mem0 import Memory; m = Memory.from_config(json.load(open('mem0.json')))`.
- The `memory` tool's 2,200-char budget is SEPARATE from mem0 FAISS storage (unlimited). See Runtime Query Protocol below.

**Fix all "use mem0_add / mem0_search tool" instructions** → replace with either `memory` tool or direct Python `Memory.from_config()`.

### Ollama auto-start (Windows Registry) — kills the "plugin cached not initialized" race (2026-07-08)

The biggest cause of "Mem0 backend not initialized: Failed to connect to Ollama" is Ollama not running when Hermes boots. Fix permanently by adding Ollama to Windows auto-start via Registry (no Startup-folder .bat needed):

```bash
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "Ollama" /t REG_SZ /d "\"C:\Users\khoans\AppData\Local\Programs\Ollama\ollama.exe\" serve" /f
```
Verify: `reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" | grep -i ollama`. Reboot → Ollama listens on :11434 automatically. mem0 FAISS needs NO separate process (in-process) — only Ollama must be up.

### Cross-profile FAISS swap — personal_profile deepseek LLM gotcha (2026-07-08)

When swapping all 3 profiles (warren / stock / personal) to FAISS:
- **Backup each** `mem0.json` → `mem0.json.bak` first.
- **personal_profile** originally used `"llm": {"provider": "deepseek", ...}` with NO `api_key` in mem0.json → mem0 falls back to OpenAI (error). **Fix:** set mem0 `llm` to `ollama` (consistent with other profiles) so mem0 init works. This only affects mem0 fact-extraction — the profile's chat LLM (deepseek via `config.yaml`) is untouched.
- **stock-profile** had flat schema already (just `qdrant` → `faiss` + add `path`).
- Verify each with `Memory.from_config()` + `m.add()` + `m.search()` (see Verification below). Expect `<profile>/mem0_faiss/mem0.faiss` + `mem0.json` on disk.

### Package name trap

`pip install mem0` → fails. Use `pip install mem0ai`.

### Config file trap

The `hermes config set mem0.qdrant_url http://localhost:6333` command writes to config.yaml's `mem0:` block, which the Hermes mem0 plugin **never reads**. The plugin reads from `$HERMES_HOME/mem0.json`.

The only relevant `config.yaml` key is:
```yaml
memory:
  provider: mem0    # Switches from builtin to mem0
```

### sed greedy trap — `provider: ''` appears in multiple sections

When setting `memory.provider: mem0` via sed/grep, `provider: ''` is NOT unique to the memory section. In Hermes config.yaml it also appears under `delegation:` and `image_gen:` (and potentially more sections).

**❌ Wrong — replaces ALL occurrences:**
```bash
sed -i "s/provider: ''/provider: mem0/" config.yaml
# → Breaks delegation.provider AND image_gen.provider
```

**✅ Safe approaches (pick one):**

1. **Line-specific sed** (know the line number first):
   ```bash
   grep -n "  provider:" ~/AppData/Local/hermes/profiles/warren-profile/config.yaml
   # Then target only the memory section line:
   sed -i '419s/provider: ''/provider: mem0/' config.yaml
   ```

2. **`hermes config set`** (always targets the right section):
   ```bash
   hermes config set memory.provider mem0
   ```

3. **Context-aware sed** (match surrounding lines):
   ```bash
   sed -i '/^memory:/,/^[a-z]/{s/provider: ''/provider: mem0/}' config.yaml
   ```

**Verify after any method:**
```bash
grep -n "provider: mem0" config.yaml
# Should show ONLY the memory section line
```

### Slow first write

First `mem0_add` / sync_turn takes ~3 minutes with local Ollama LLM. The Hermes plugin runs everything in background threads, so the agent isn't blocked — but the data won't be searchable until the background thread completes.

**This is normal.** Subsequent writes are faster (warm cache).

### Orphan Docker Qdrant data (embedded mode users)

This is one of the most confusing situations. If you see a **Docker Qdrant container running** with a `mem0` collection containing N points, but `mem0_search` returns "No relevant memories found" — you're using embedded Qdrant, and the Docker container is a leftover from a previous setup. mem0 ignores it entirely.

**How to tell:**
```bash
grep -E '"path"|"url"' $HERMES_HOME/profiles/<profile>/mem0.json
# → "path": "..." means embedded (your data is on-disk, not in Docker)
# → "url": "http://localhost:6333" means Docker (your data IS in the Docker container)
```

**Docker Qdrant has its own lifecycle.** A running `docker ps --filter name=qdrant` means nothing about whether mem0 is connected to it.

**To clean up orphan Docker data** (optional — data is harmless, delete the container if you want):
```bash
docker stop qdrant && docker rm qdrant
```
Or keep it — it won't interfere with embedded mem0 at all.

### Qdrant container auto-restart (Docker Qdrant only)

Enable auto-restart to survive reboots:
```bash
docker update --restart unless-stopped qdrant
```

Embedded Qdrant auto-manages its own lifecycle — nothing to configure.

### MSYS/git-bash path mangling on Windows (agent-facing)

When running Windows commands from a git-bash terminal (Hermes `terminal` tool on Windows), MSYS auto-converts Unix-style paths and flags. **This breaks `taskkill`, `cmd.exe`, and any command using `/flag` syntax.**

| What you type | What MSYS sends | Result |
|--------------|-----------------|--------|
| `taskkill /F /PID 123` | `taskkill F:/ PID 123` | ❌ "Invalid argument - 'F:/'" |
| `cmd.exe /c "script.bat"` | `cmd.exe C:/ "script.bat"` | ❌ Path mangled |
| `cmd.exe //c "script.bat"` | `cmd.exe /c "script.bat"` | ⚠️ Works for simple commands |
| `powershell.exe -Command "..."` | unchanged | ✅ **Most reliable** |

**Rule:** When you need to run Windows-native commands (taskkill, sc, reg, etc.) from the Hermes terminal, use `powershell.exe -Command "..."` to bypass MSYS path conversion entirely.

### Plugin caches init state — restart required (all backends)

**Critical:** The Hermes mem0 plugin initializes ONCE at session start. If Qdrant (or Ollama) is down at that moment, the plugin caches a permanent "not initialized" error and **never retries** — even after the service comes back up.

**Docker Qdrant symptoms:**
```
mem0_search → "Mem0 backend not initialized: [WinError 10061] No connection could be made because the target machine actively refused it."
```
Even though `curl localhost:6333/healthz` returns "healthz check passed."

**Embedded Qdrant symptoms:** No port/docker errors — the embedded driver either inits or doesn't at session start. If Ollama is down, you'll see Ollama connection errors.

**Fix sequence (all backends):**
1. Start the down service: `ollama serve` (if Ollama); `docker start qdrant` (if Docker Qdrant)
2. Verify: `curl -s http://localhost:11434/api/tags` → models listed (Ollama check)
3. **Restart Hermes gateway** so the mem0 plugin re-initializes with all services up

A `/new` session does NOT fix this — the gateway process itself needs restarting.

**On Windows (git-bash terminal):** `hermes restart gateway` may not work if the gateway was started via Startup folder `.bat`. Use PowerShell:
```powershell
powershell.exe -Command "Stop-Process -Name pythonw -Force; Start-Sleep 3; Start-Process -FilePath 'cmd.exe' -ArgumentList '/d /c C:\\Users\\khoans\\AppData\\Local\\hermes\\gateway-service\\Hermes_Gateway.cmd' -WindowStyle Minimized"
```
Or double-click `Restart_Hermes_Gateway.bat` on Desktop (see `references/windows-auto-start-reliability.md` for setup).

### Hermes mem0 TOOLS fail with "Failed to connect to Ollama" even when services are UP (2026-07-07)

**Distinct from the "plugin cached not initialized" pitfall above.** In that one, services were DOWN at session start. Here, **both Ollama (11434) and Qdrant (6333) are confirmed alive** — `curl localhost:11434/api/tags` returns models, `curl localhost:6333/collections` returns `mem0`/`mem0_entities`/`mem0migrations` — yet `mem0_add` / `mem0_list` STILL error with:

```
Mem0 backend not initialized: Failed to connect to Ollama. Please check that Ollama is downloaded, running and accessible...
```

**Root cause:** mem0ai 2.0.7 embedder-factory bug — the plugin builds the embedder client incorrectly and surfaces a misleading Ollama error, even though Ollama responds fine to direct REST calls. The Hermes *tool layer* is broken; the *infrastructure* is not.

**Diagnostic sequence (don't trust the error message):**
```bash
curl -s -m 5 http://localhost:11434/api/tags | head -c 100   # Ollama up? expect models
curl -s -m 5 http://localhost:6333/collections | head -c 200 # Qdrant up? expect collections
curl -s -m 5 http://localhost:6333/collections/mem0 | head -c 300  # collection + dims
```
If 1+2 return healthy JSON → the Hermes *tool* is the problem, not the stack.

**Fix (verified 2026-07-07): bypass the plugin entirely — write directly to Qdrant REST + embed via Ollama.** This is the SAME bypass as `references/cross-profile-mem0-write-via-qdrant-api.md`, but it applies to **same-profile writes too**, not just cross-profile. Do NOT waste time on `mem0_add` tool, `Memory.from_config()`, or gateway restart — they all route through the broken plugin.

**Ready-to-run:** `scripts/mem0_bulk_push.py` — embeds facts via Ollama `nomic-embed-text`, PUTs points to Qdrant `mem0` collection. Verified: pushed 23 facts (warren user_id count 40→49, search returned correct fact).
```bash
python scripts/mem0_bulk_push.py facts.json --user-id warren   # facts.json = JSON array of strings
python scripts/mem0_bulk_push.py --facts "fact one" "fact two" --user-id warren
```
**Verify the push** (direct Qdrant, not the broken tool):
```bash
python -c "
import urllib.request, json
f={'must':[{'key':'user_id','match':{'value':'warren'}}]}
r=urllib.request.urlopen(urllib.request.Request('http://localhost:6333/collections/mem0/points/count',data=json.dumps(f).encode(),headers={'Content-Type':'application/json'}),timeout=10)
print('warren count:', json.loads(r.read())['result']['count'])
"
```
> **Lesson:** When mem0 tooling errors, ALWAYS verify the underlying services with raw `curl` before assuming the stack is down. The Hermes mem0 tool error messages are unreliable here.

### Qdrant 1.18 native Windows: no `--storage-path`, use `--config-path`

Qdrant 1.18.x on Windows removed `--storage-path`. Using it gives:
```
error: unexpected argument '--storage-path' found
```

**Solution:** Create a `config.yaml` with absolute `storage.storage_path` and pass it via `--config-path`:

```yaml
storage:
  storage_path: C:\Users\khoans\.hermes\qdrant
  performance:
    max_search_threads: 1
  optimizers:
    default_segment_number: 2
service:
  host: 0.0.0.0
  http_port: 6333
  grpc_port: 6334
```

```bash
qdrant.exe --config-path "C:\Users\khoans\.hermes\qdrant\config.yaml"
```

**IMPORTANT:** Use an **absolute path** for `storage_path`, not `.` (relative). Qdrant's working directory is unpredictable when launched via `Start-Process` or `start /B /MIN` — a relative `storage_path: .` may resolve to Desktop, System32, or the exe dir depending on how it was launched. An absolute path guarantees the same storage location every time.

A `config.yaml` placed at `$STORAGE/config.yaml` with absolute `storage_path` pointing to itself makes `--config-path` point to the same directory as the data — clean and self-contained.

### Qdrant native Windows health endpoint

Docker Qdrant and native Windows Qdrant differ on health-check endpoints:

| Variant | Endpoint | Response |
|---------|----------|----------|
| Docker Qdrant | `GET /healthz` | `"healthz check passed"` |
| Native Windows (1.18.x) | `GET /` | `{"title":"qdrant - vector search engine","version":"1.18.2",...}` |
| Native Windows (1.18.x) | `GET /collections` | Lists collections (confirms server is alive) |

**For native Windows Qdrant, use `curl -s http://localhost:6333/` (root) instead of `/healthz`.**

### Native Windows default storage path

When `qdrant.exe` runs WITHOUT `--config-path`, it stores data in `./storage/` relative to its working directory — NOT in the exe directory.

If `qdrant.exe` lives in `C:\Users\khoans\AppData\Local\qdrant\` and is run from the shell's cwd, data goes to `$CWD/storage/`. To ensure consistent storage, always pair a config.yaml with `storage_path:` pointing to the target directory.

The old data in `~/.hermes/qdrant/` (pre-1.18 format) has collections as flat subdirectories (`warren/`, `stock_profile/`) — incompatible with Qdrant 1.18's `./storage/collections/` layout. If migrating, snapshot+restore or restart fresh.

**On Linux/macOS:** `hermes gateway restart` or from the GUI restart button.

> **Windows auto-start reliability:** For the full recipe to prevent this race condition on every boot — Ollama Startup folder, Gateway wait-loop, restart script — see `references/windows-auto-start-reliability.md`.

### Quick health check & search

```bash
# Quick search without Hermes tools
python3 $PROFILE/scripts/mem0_search.py "query"
```

### Quick health check

After the 2026-07-08 Qdrant→FAISS swap, Warren's profiles use **FAISS** (in-process, no server). Health check = Ollama + FAISS index files only. There is NO Qdrant endpoint to curl — `curl localhost:6333` will fail by design.

Use the `mem0-status.sh` script (in `stock-profile/scripts/`):
```bash
bash stock-profile/scripts/mem0-status.sh
# → shows Ollama status + faiss_path for all 3 profiles
```

Or manually:
```bash
# Ollama (only external service)
curl -so /dev/null http://localhost:11434/api/tags && echo "Ollama: OK" || echo "Ollama: DOWN"

# FAISS index files (per profile) — prove backend is real
ls "$HERMES_HOME/profiles/<profile>/mem0_faiss/" 2>/dev/null && echo "FAISS index: OK" || echo "FAISS index: missing (created on first write)"
```

**Note:** Embedded Qdrant has NO HTTP endpoint. `curl localhost:6333` will fail. For embedded, the `collection/` directory is created dynamically on first mem0 write — an empty directory just means nothing stored yet, which is normal.

### Full round-trip verification

After infrastructure checks pass, prove the pipeline actually works end-to-end:

1. **Write a test fact:**
   ```
   mem0_add(content="mem0 round-trip test — $(date)")
   ```
2. **Search for it:**
   ```
   mem0_search(query="round-trip test")
   ```
   → Expect score ≥0.7 and the exact text returned.
3. **Clean up:**
   ```
   mem0_delete(memory_id="<id from search>")
   ```

This catches silent failures that infrastructure checks miss:
- **Wrong user_id config** — `mem0_add` writes to wrong namespace, `mem0_search` finds nothing
- **Embedding mismatch** — write succeeds but search returns garbage scores
- **Plug-in never initialized** — both calls error ("Mem0 backend not initialized")
- **Collection locked/unwritable** — write succeeds but search returns nothing

**Important:** for a fresh profile, `mem0_list()` returning 0 memories is NORMAL. No data has been written yet. The collection is created on first `mem0_add`, not at session init. A clean `mem0_list` is not a failure signal — only a failed round-trip is.

### Cross-profile backend migration MUST include skill/script/SOUL.md audit (2026-07-08)

When you swap a backend across multiple profiles, `mem0.json` is NOT the only place the old backend lives. After swapping all 3 `mem0.json` files, you MUST grep the surrounding surface for stale references and fix them, or agents will hit dead Qdrant calls later:

- **Per-profile `SOUL.md`** — lines like `| mem0 | Qdrant (vector DB) |` and `Trước mỗi lần gọi mem0_add` must become `FAISS (in-process vector DB)` / `memory tool`.
- **Skill `SKILL.md`** (e.g. `mem0-search`) — rewrite to drop Qdrant REST bypass sections; keep a one-line "Qdrant removed, deprecated" note so old docs don't mislead.
- **Shell scripts** (`mem0-status.sh`, `mem0-on.sh`, `mem0-off.sh`) — remove `qdrant.exe` / `localhost:6333` start/stop logic. `mem0-status.sh` should read `vector_store.config.path` (flat schema, NOT the old `oss` wrapper).
- **Python scripts** (`mem0_search.py`) — replace `requests`/urllib Qdrant REST calls with `Memory.from_config(cfg)` + `m.search(...)`.

**Warren's deletion rule (explicit):** "xóa = xóa hẳn" — when removing a deprecated component, DELETE the file (e.g. `mem0-direct-qdrant.py`, `references/save-workaround.md`), do NOT leave a "deprecated note" stub. The only exception is keeping a one-line "X removed" note inside a still-active doc for historical clarity.

**Verification after audit:** re-grep the edited paths for `qdrant|localhost:6333|mem0_add|mem0.ps1|QDRANT_URL|search_qdrant`. Intentional mentions like "Qdrant fully removed" / "do NOT use Qdrant REST" are OK; live config/logic references are not. Then RUN the rewritten script once (e.g. `mem0_search.py -p warren "FAISS"`) to prove zero Qdrant calls.

### Verify shell scripts from Hermes terminal, NOT from a python subprocess (2026-07-08)

`bash` is available in the Hermes `terminal` tool's git-bash layer, but a Python `subprocess.run(["bash", ...])` launched from the hermes venv **cannot find bash** (MSYS path `/usr/bin/bash` is virtual; no `bash.exe` on Windows PATH for the subprocess). Running `bash -n script.sh` or `bash script.sh` directly in the Hermes terminal works. For ad-hoc verification scripts under `%TEMP%` with a `hermes-verify-` prefix: write them as `.py` but execute them via the Hermes `terminal` tool (call `python.exe script.py`) — do NOT try to spawn bash from inside the python script. This also satisfies the "fresh passing verification evidence" requirement after code edits.

The recurring error `Storage folder ... is already accessed by another instance of Qdrant client` (embedded Qdrant single-process lock) was the #1 reason for "use Qdrant Server" recommendations. **After the Qdrant→FAISS swap, this class of error cannot occur** — FAISS is in-process with no server, and mem0 2.0.10's FAISS backend handles multi-process access within the same Python process cleanly.

Do NOT reintroduce Qdrant to "fix" a concurrency issue. If a Hermes process reports a mem0 init failure after the swap, the cause is **Ollama down at boot** (see Ollama auto-start pitfall), not a vector-store lock.

- Stale reference `references/qdrant-concurrent-access-root-cause.md` is kept for archival only — its conclusion (use Qdrant server) is **obsolete for Warren's setup**.

### mem0_delete requires full UUID, not short ID

`mem0_list` returns entries with both a `short_id` (e.g. `2ed46937`) and a full UUID (e.g. `2ed46937-d1ee-496c-988f-f74d992b5b40`). **`mem0_delete` requires the FULL UUID.**

Passing the short ID causes:
```
Format error in JSON body: value 2ed46937 is not a valid point ID, valid values are either an unsigned integer or a UUID at line 1 column 60
```

After 3+ such errors in one turn, mem0 enters "temporarily unavailable" mode and refuses all operations. To recover, restart Qdrant:

```powershell
# 1. Kill current qdrant process
taskkill //F //IM qdrant.exe

# 2. Wait a moment
Start-Sleep -Seconds 2

# 3. Start qdrant as background service process
# Use the terminal tool: terminal(background=true, command="cd /c/Users/khoans/AppData/Local/qdrant && ./qdrant.exe --uri http://localhost:6333")

# 4. Verify health
curl -s http://localhost:6333/healthz
# → "healthz check passed"

# 5. Retry mem0 operations — now with full UUIDs
mem0_delete(memory_id="<full-uuid-here>")
```

**Why it works:** The `start_qdrant.bat` runs qdrant inline (it blocks the batch until qdrant exits). When launched via `cmd.exe /c`, qdrant is killed on batch exit. Running `qdrant.exe` directly as a background terminal process keeps it alive independently.

### DeepSeek LLM requires api_key

Using DeepSeek as the LLM provider in `mem0.json`? You MUST include `"api_key"` in the config. Without it, mem0 will fail with:

```
Missing credentials. Please pass an `api_key`, `workload_identity`, `admin_api_key`,
or set the `OPENAI_API_KEY` or `OPENAI_ADMIN_KEY` environment variable.
```

**Why:** Unlike Ollama (which runs locally), DeepSeek is a cloud API — mem0 needs a valid key to call it.

**Fix options (pick one):**

1. **Add api_key to mem0.json** (works immediately):
```json
"llm": {
    "provider": "deepseek",
    "config": {
        "model": "deepseek-chat",
        "api_key": "sk-your-key-here",
        "temperature": 0.2,
        "max_tokens": 2000
    }
}
```

2. **Set DEEPSEEK_API_KEY or OPENAI_API_KEY env var** before starting Hermes.

3. **Switch to Ollama LLM** (preferred for local-only, no API key):
```json
"llm": {
    "provider": "ollama",
    "config": {
        "model": "llama3.2:3b",
        "ollama_base_url": "http://localhost:11434",
        "temperature": 0.2,
        "max_tokens": 2000
    }
}
```

**Tradeoff:** Ollama LLM is slower (~3 min first write) but zero external dependency. DeepSeek is faster but needs a valid API key that works with mem0's DeepSeek integration (the Hermes proxy at localhost:8787 does NOT apply — mem0 calls DeepSeek directly).

### PostHog warnings

`[PostHog] Multiple active PostHog clients detected...` is harmless. mem0 uses PostHog for telemetry. On local/offline setups, the warnings can be ignored.

### spaCy / fastembed warnings

```
Failed to load spaCy lemma model
fastembed not installed — BM25 keyword search disabled
```

These are non-fatal. BM25 keyword search and NLP lemmatization are optional features for advanced retrieval. Basic vector search works without them.

---

## Data Inspection — Query FAISS via mem0 Python API

The `memory(action='search')` tool only shows the **current profile's** data. To inspect memories across profiles or verify the FAISS store directly, use the mem0 Python library (bypasses the Hermes plugin lifecycle):

```python
import json, os
from mem0 import Memory
HOME = os.path.expanduser("~/AppData/Local/hermes/profiles")
for prof in ["warren-profile", "stock-profile", "personal_profile"]:
    cfg = json.load(open(f"{HOME}/{prof}/mem0.json"))
    m = Memory.from_config(cfg)
    uid = cfg.get("user_id")
    res = m.search("test query", top_k=5, filters={"user_id": uid, "agent_id": "hermes"})
    print(f"=== {prof} ({uid}) ===")
    for r in res:
        print(f"  score={r.get('score'):.2f}  {r.get('memory','')[:80]}")
```

To check the on-disk index exists (proves backend is real):
```bash
ls "$HERMES_HOME/profiles/<profile>/mem0_faiss/"   # → mem0.faiss + mem0.json
```

> **Legacy Qdrant REST queries are dead.** All `curl localhost:6333/collections/...` snippets in this skill and in `references/mem0-cross-profile-inspection.md` / `scripts/mem0_search.py` are **obsolete** post-2026-07-08. FAISS has no HTTP endpoint. Use `Memory.from_config()` + `m.search()` (vector) or grep `MEMORY.md` files (file source) instead. The MEMORY.md file-search half of `mem0_search.py` still works; the Qdrant half must be rewritten or the script will throw.

---

## On-Demand / Lightweight Operation Pattern

### Problem

mem0 OSS with **FAISS backend** (Warren's current setup — Qdrant swapped out on 2026-07-08) requires ONLY Ollama running. FAISS is in-process (no server, ~50MB, free with local Ollama). Qdrant was removed entirely — there is no `:6333` service anymore. The only external dependency is Ollama (embedder `nomic-embed-text` + LLM `llama3.2:3b` for fact extraction).

**Solution:** Set `memory.provider: ''` in all profiles (disables mem0 auto-init). Only start Ollama when Warren explicitly wants to save/query an important fact, then stop. (Ollama is also set to auto-start via Windows Registry — see Ollama auto-start pitfall — so for most sessions it is already up and FAISS works with zero manual steps.)

### What works when services are DOWN

| Operation | Works? | Why |
|-----------|--------|-----|
| `memory` tool (FAISS-backed add/search) | ❌ (fails) | Needs Ollama at call time |
| Background prefetch (auto) | ❌ Fails silently | Background thread — no error shown |
| Background sync (auto per turn) | ❌ Fails silently | Background thread — no error shown |
| Session-end extract (auto) | ❌ Fails silently | Background thread — no error shown |
| Built-in `memory` tool context injection | ✅ Always | File-based, no services needed |
| `session_search` | ✅ Always | Reads Hermes session DB |

> Hermes 0.18.2 has NO `mem0_add`/`mem0_search` plugin tools. The `memory` tool IS the mem0 interface (FAISS backend). Direct Python `Memory.from_config()` is the fallback for verification/bulk ops.

### What works when services are UP mid-session

**Critical nuance: depends on `provider` config value at session start.**

| Operation | `provider: ''` (disabled) | `provider: mem0` (plugin tried & failed) |
|-----------|--------------------------|----------------------------------------|
| `mem0_add` tool | ✅ Yes — no plugin to fail | ❌ Fails — plugin cached "not initialized" |
| `mem0_search` tool | ✅ Yes | ❌ Same |
| Python `mem0.Memory.from_config()` (direct) | ✅ Yes | ✅ Yes — bypasses plugin entirely |
| Auto prefetch/sync/extract | ❌ No plugin | ❌ |
| Built-in `memory` tool | ✅ Always | ✅ Always |

> **Key insight:** The Hermes `mem0_add`/`mem0_search` **TOOLS** go through the mem0 plugin layer. If the plugin failed to initialize at session start (because services were down), it caches "Mem0 backend not initialized" and **never retries** — even after starting services mid-session. Only direct Python calls via `mem0.Memory.from_config()` bypass this.
>
> With `provider: ''` there is no plugin to fail — the tools connect to Qdrant directly on every call. This is the true on-demand pattern.
>
> **If you're mid-session with `provider: mem0` and the plugin is stuck**, see "Recovery: direct Python call when plugin is cached" below.

### Recovery: direct Python call when plugin is cached

When the Hermes mem0 plugin cached "not initialized" mid-session, the `mem0_add`/`mem0_search` tools are dead until gateway restart. Workaround: call mem0 library directly from Python.

**Pattern (verified 2026-06-27):**

1. Start Qdrant + Ollama (if not already running)
2. Write a temporary Python script:
```python
import json
from mem0 import Memory

with open(r"$HERMES_HOME/profiles/<profile>/mem0.json") as f:
    cfg = json.load(f)

# mem0 2.0.10 FLAT schema — use cfg directly (NO cfg['oss'] wrapper)
m = Memory.from_config(cfg)

# Add
m.add("fact to save", user_id=cfg['user_id'], agent_id="hermes")

# Search
results = m.search("query", top_k=5, filters={"user_id": cfg['user_id']})
for r in results:
    print(f"Score: {r.get('score', 'N/A')} → {r.get('memory', '')[:80]}")
```
3. Run with `python3 <script.py>` — allow up to 3 min for first write (Ollama LLM cold start)
4. Verify via `mem0_search.py` (standalone script, not tool)
5. Delete the temp script

**Why `Memory.from_config()` works:** It creates a fresh mem0 client that connects to Qdrant + Ollama independently — no Hermes plugin involved.

### 3 ways to use it (Warren's preference, ranked by ease)

**Cách C — Nói Hermes làm hết (rảnh tay nhất, khuyên dùng):**
Warren nói 1 câu trong Hermes:
> "mem0 ơi, bật giúp tôi nhớ là ..."

Agent tự động (trong 1 turn):
1. `terminal` → start Qdrant + Ollama (call .ps1)
2. Thử `mem0_add(content="...")` → nếu fail do plugin cached → fallback: viết script Python tạm, chạy `Memory.from_config()` trực tiếp
3. Hoặc `mem0_search(query="...")` → dùng `mem0_search.py` nếu tool fail do plugin cached
4. `terminal` → stop services
5. Báo "Xong rồi!"

**Cách A — Double-click file trên Desktop:**
- Double-click `mem0-on.bat` → chờ 5-10s
- Vào Hermes: "mem0 ơi nhớ là ..."
- Double-click `mem0-off.bat`

**Cách B — Gõ lệnh PowerShell:**
```powershell
& "$env:USERPROFILE\Desktop\mem0-on.bat"
# ... dùng Hermes lưu ...
& "$env:USERPROFILE\Desktop\mem0-off.bat"
```

### Pre-built scripts

**Windows (PowerShell):** `scripts/mem0.ps1` — handles both On/Off, auto-creates collections. Deployed to Desktop as `mem0-on.bat` + `mem0-off.bat` (thin wrappers).
**Linux/macOS:** `scripts/mem0-on.sh` and `scripts/mem0-off.sh` — **Ollama-only** (FAISS is in-process, no Qdrant server to manage). Patched 2026-07-08 to delete all Qdrant start/stop logic.

```
Desktop\
├── mem0.ps1        ← Engine: bật/tắt Qdrant + Ollama, auto-create collections
├── mem0-on.bat     ← Thin wrapper: powershell -File mem0.ps1 -Action On
└── mem0-off.bat    ← Thin wrapper: powershell -File mem0.ps1 -Action Off
```

`.bat` là thin wrappers — chỉ để double-click thuận tiện. Logic chính trong `.ps1`:
- Kiểm tra service qua HTTP health check (tránh start trùng)
- Start Qdrant với `--config-path` trỏ đến `config.yaml` có `storage_path` tuyệt đối
- Start Ollama serve
- Auto-create Qdrant collections `mem0` + `mem0_entities` (768-dim Cosine, BM25 sparse) nếu chưa tồn tại
- Wait up to 25s cho Qdrant (first start chậm do load data), 15s cho Ollama
- Stop: `Stop-Process -Force` cả 2

See `scripts/mem0.ps1` for the engine, `templates/mem0-on.bat` and `templates/mem0-off.bat` for Desktop wrappers.

**Chạy từ Hermes terminal (agent call pattern):**

Trên Windows (git-bash), MSYS path conversion có thể break `%USERPROFILE%` và `/f` flags. Pattern đã verified:

```bash
# Bật — dùng full path để tránh MSYS
powershell.exe -ExecutionPolicy Bypass -File "C:\Users\khoans\Desktop\mem0.ps1" -Action On

# Lưu memory
mem0_add(content="important fact")

# Tra cứu
mem0_search(query="important")

# Tắt
powershell.exe -ExecutionPolicy Bypass -File "C:\Users\khoans\Desktop\mem0.ps1" -Action Off
```

Hoặc dùng `cmd.exe //c` (double-slash để bypass MSYS):
```bash
cmd.exe //c "%USERPROFILE%\Desktop\mem0-on.bat"
```
```

> **Verified 2026-06-27:** Full round-trip: on → `mem0_add` → `mem0_search` (score 0.81) → off took ~15s.

### Auto-create Qdrant collections on first start

Khi chạy Qdrant lần đầu với storage mới, collection `mem0` chưa tồn tại → `mem0_add` fail với:
```
404: Collection `mem0` doesn't exist!
```
Script `.ps1` gọi `Invoke-RestMethod -Method Put` để tạo collections via REST API nếu chưa có. Config matching mem0 OSS spec:
```json
{
  "vectors": {"size": 768, "distance": "Cosine"},
  "sparse_vectors": {"bm25": {"modifier": "idf"}}
}
```

## Runtime Query Protocol — mem0 vs Built-in `memory` Tool

### Critical distinction (Warren repeated correction)

Hermes has TWO separate memory systems:

| Aspect | Hermes `memory` tool (context injection) | mem0 / FAISS |
|--------|------------------------------------------|---------------|
| What it is | Tool in SOUL.md -- save/recall durable facts across sessions | Full vector DB -- FAISS (in-process) + Ollama embeddings |
| Visibility | Injected into EVERY turn automatically (2200 char limit) | NOT auto-injected. Must be queried explicitly |
| Contents | User profile + procedural memory (compressed by curator) | All `memory`-tool writes (FAISS-backed) |
| Search | No semantic search -- flat key-value | Vector search with scores |
| When Warren says 'mem0' | Do NOT rely on this alone | MUST query FAISS directly |

### Critical clarification: context budget != storage limit

When `memory()` tool reports e.g. '2,126/2,200 chars' -- that is the **context injection budget** (entries auto-injected into the prompt), NOT a storage limit.

| Term | What it is | Limit |
|------|-----------|-------|
| Context injection budget | Entries auto-fed into Hermes prompt each turn | 2,200 chars (`memory_char_limit`) |
| Storage (Qdrant / file) | All entries ever saved | Unlimited (867 GB free on this machine) |

What happens when budget is full:
- `memory()` tool rejects new adds or asks to consolidate
- Existing entries are **never lost** -- they just stop being auto-injected
- They remain searchable via `mem0_search` or `mem0_search.py`
- Fix: remove low-value entries, or increase `memory_char_limit` in config.yaml

Hermes `memory` (context injection) does NOT mirror mem0 Qdrant. They are independent stores.

**Lesson from 2026-06-27 (Warren: "sao tao nhắc mem0, mà mày ko search trong đó"):**
- Hermes `memory` (context injection) does NOT mirror mem0 Qdrant. They are independent stores.
- Built-in `memory` is curated/compressed — entries like "Warren thích gái đẹp" and "GAS" were in mem0 but never made it into context memory due to char limits or curator pruning.
- **When Warren's query implicates mem0** (says "mem0", "nhớ", "lưu cái gì đó", "trong mem0 có...", or asks about stored preferences/facts that might not be in recent context) → search mem0 FIRST via `mem0_search` tool or `scripts/mem0_search.py`.

**Command priority when Warren asks about stored info (Hermes 0.18.2)**

> NOTE: `mem0_search` / `mem0_add` PLUGIN TOOLS do NOT exist in 0.18.2. Use the `memory` tool (FAISS-backed) or `scripts/mem0_search.py` (direct Qdrant/vector + MEMORY.md).

1. **If query explicitly mentions "mem0"** → use `memory(action='search')` tool OR `scripts/mem0_search.py "query"`
2. **If query is "Warren thích gì" / "tao thích gì" / about own preferences** → search mem0 FIRST via `memory` tool or `mem0_search.py` (Warren's actual data may be there, not in context memory), THEN supplement with context memory
3. **If query is about current operations / today's work / last session** → `session_search` (Hermes session DB)
4. **If query is about a fact you know from context memory** → you can answer from context, but verify with mem0 if uncertain

**Warren "thích gì" case:** In this session, mem0 returned `score: 0.84 — Warren thích gái đẹp` and `score: 0.72 — Warren thích đầu tư vào cổ phiếu GAS nhiều lắm` — data that was NEVER in context memory. Relying on context memory alone gives an incomplete picture.

### Script: `scripts/mem0_bulk_push.py` (write-side bypass)

Companion to `mem0_search.py` for the **write** path. When the Hermes `mem0_add` tool errors with "Failed to connect to Ollama" despite both services being up (mem0ai 2.0.7 embedder-factory bug), use this to push facts directly to Qdrant via Ollama embeddings. See pitfall "Hermes mem0 TOOLS fail with 'Failed to connect to Ollama' even when services are UP" above.

### Script: `scripts/mem0_search.py`

A standalone Python script that searches **BOTH** MEMORY.md (file) + Qdrant (vector) — across all 3 profiles (warren, personal, stock). Works independently of Hermes mem0 plugin lifecycle.

**Không cần `requests` — dùng `urllib.request` (stdlib).**

**Usage:**
```bash
python3 mem0_search.py "POWER LUNCH"              # warren (default)
python3 mem0_search.py -p stock "PVD"              # stock profile
python3 mem0_search.py -p personal "health"        # personal
python3 mem0_search.py -k 10 "LU5"                 # override top-k
```

**How it works (REWRITTEN 2026-07-08 to FAISS):** Source 1 = MEMORY.md keyword grep (unchanged). Source 2 = vector search via `Memory.from_config(cfg)` + `m.search(filters={"user_id":...,"agent_id":"hermes"})` — NO Qdrant REST, NO urllib. Verified working across all 3 profiles (warren/stock/personal) same session. The old Qdrant-REST version was deleted. If you see `localhost:6333` in this script, it is stale — rewrite to `Memory.from_config()`.
1. **Source 1 (MEMORY.md):** keyword grep — splits entries by `§` delimiter, ranks by keyword match count. Instant (~0.000s).
2. **Source 2 (FAISS via mem0 Python API):** vector search — loads `mem0.json`, inits `Memory.from_config()`, embeds query via Ollama `nomic-embed-text`, searches the FAISS index (per profile `mem0_faiss/` dir) by user_id. (Pre-2026-07-08 this used Qdrant REST — that path is dead; rewrite the script's vector half if it still has `localhost:6333` calls.)
3. **Merge + dedup:** interleaves results by score, normalizes duplicates by text prefix.
4. **Output:** source badge `[📄=file / 🔍=vector]`, score, text, metadata (channel, created time, ID).

**Why use this instead of `mem0_search` tool?** Use the built-in `mem0_search` when the Hermes plugin is active. Use `mem0_search.py` for: debugging, cross-profile search, or when the plugin isn't initialized (`provider: ''` mode). The file source (MEMORY.md) is a bonus this script has that the plugin tool doesn't.

---

### Alternative: built-in memory as the lightweight default

| Aspect | Built-in `memory` | mem0 OSS (on-demand) |
|--------|------------------|---------------------|
| Services needed | None | Qdrant + Ollama (start/stop) |
| RAM | 0 | ~100MB khi đang dùng, 0 khi off |
| Semantic search | No (flat key-value) | Yes (vector search) |
| Auto-extract from conversation | No (manual save only) | N/A (disabled in on-demand mode) |
| Cross-session context injection | Yes (system prompt) | Only for manually saved facts |
| Cost | Free | Free |

**Use built-in memory for:** quick notes, preferences, decisions — anything Warren wants remembered without overhead.
**Fire up mem0 for:** semantically searching old facts, or when the built-in 2,200-char limit isn't enough.

### Cross-reference

- `hermes-profile-memory-architecture` — how memory layers stack (builtin + mem0)
- `performance-optimization` — general Hermes resource tuning

### Reference files (this session)

- `references/on-demand-lightweight-mem0-2026-06-27.md` — full session details: why PowerShell, auto-create collections, Qdrant 1.18 Windows quirks, 3 user-facing workflows, verified round-trip output
- `references/lightweight-vector-backend-research-2026-07-08.md` — Gbrain / zvec / Tencent / LanceDB / FAISS verdicts vs Warren's laptop/cost/24-7 constraints; why FAISS won
- `references/cross-profile-faiss-swap-2026-07-08.md` — exact cross-profile swap execution: personal deepseek fix, stale-reference audit list, mem0_search.py rewrite, shell-verify gotcha
- `references/hermes-desktop-memory-panel-hindsight.md` — what the Desktop "Memory Provider Panel" actually is (Hindsight config form), verified source + commits (2026-07-19)
- `scripts/mem0.ps1` — the engine script (PowerShell, handles both On/Off, auto-creates collections)

## Enable mem0 on a New / Disabled Profile — Activation Checklist (0.18.2-valid)

When a profile currently has `memory.provider: ''` (or builtin) and you need to turn on mem0 + FAISS (mirroring another profile like warren-profile):

1. **Verify Ollama is running** (mem0 needs it at call time). If installed but down, start it in a `background=true` terminal (NOT `&` foreground):
   ```bash
   cd "C:/Users/khoans/AppData/Local/Programs/Ollama" && ./ollama serve
   ```
   Then health-check: `curl -s http://localhost:11434/api/tags` → expect `llama3.2:3b` + `nomic-embed-text` listed.
2. **Create `mem0.json`** in the profile dir (copy from a working profile, change `path` to `<profile>/mem0_faiss`). Flat schema, FAISS provider. See template above.
3. **Set provider via `hermes config set`** — direct file edit of config.yaml is BLOCKED by a security guard ("cannot modify security-sensitive configuration"). Use:
   ```bash
   hermes config set --profile <profile> memory.provider mem0
   hermes config set --profile <profile> memory.write_approval false   # auto-save ON (no approval prompt)
   ```
4. **Confirm with `mem0-status.sh`** (in profile's `scripts/`):
   ```bash
   bash <profile>/scripts/mem0-status.sh   # → Ollama: ✅ + faiss_path=<profile>/mem0_faiss
   ```
5. **Test write via the `memory` tool** (NOT `mem0_add` — that plugin tool does NOT exist in 0.18.2). `memory(action='add', content='...')`, then `memory(action='search', ...)`.
6. **Verify FAISS index files on disk** (proves backend is real, not just config):
   ```bash
   ls "<profile>/mem0_faiss/"   # → mem0.faiss + mem0.json
   ```

> **Ollama must stay up** for mem0 writes; FAISS itself needs no server. Set Windows Registry auto-start if Ollama keeps dying.
> **SSOT note (Warren 2026-07-08):** built-in `memory` auto-save ON; `STOCK_MEMORY.md` (vault) is the absolute SSOT and wins on any conflict with built-in memory; mem0+FAISS is the active durable store.

## Verification

After setup, test with a direct Python check (flat schema, mem0 2.0.10):

```python
from mem0 import Memory
import json

with open('$HERMES_HOME/mem0.json') as f:
    cfg = json.load(f)   # flat: vector_store / llm / embedder at top level

m = Memory.from_config(cfg)
results = m.search('test query', top_k=5, filters={'user_id': 'your_user_id'})
print(f'Found {len(results)} results')
```
> If init raises `OpenAIError: api_key ...` → your mem0.json still has the `oss` wrapper or is missing `llm`/`embedder`. See "CRITICAL: mem0 2.0.10 config is FLAT" above.
> Hermes 0.18.2 exposes mem0 via the `memory` tool, NOT `mem0_add`/`mem0_search` plugin tools. See "Hermes 0.18.2 has NO mem0_add tools" above.

Or in Hermes, new session → `mem0_search(query="test")`.
