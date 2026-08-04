# Cross-Profile FAISS Swap — Execution Log (2026-07-08)

Verified recipe for migrating ALL 3 Hermes profiles (warren / stock / personal)
from Qdrant → FAISS in-process. Companion to the "Swap Qdrant → FAISS" pitfall in
SKILL.md; this file captures the exact per-profile quirks + the search-script rewrite.

## Per-profile mem0.json state BEFORE swap

| Profile | Schema | vector_store | Issue |
|---------|--------|--------------|-------|
| warren-profile | flat | `qdrant` + `url` | already swapped earlier this session |
| stock-profile | flat | `qdrant` + `url` | just change provider→faiss, add `path`, drop `url` |
| personal_profile | `oss` wrapper (OLD) | `qdrant` | rewrite to flat; ALSO had `llm: deepseek` with NO api_key → mem0 fallback OpenAI error |

## personal_profile deepseek LLM fix

Original mem0.json LLM block used `"provider": "deepseek"` with no `api_key` →
mem0 ignores it, falls back to OpenAI, raises `api_key client option must be set`.
Fix: set mem0 `llm` to `ollama` (consistent with other 2 profiles). This ONLY
affects mem0 fact-extraction LLM — the profile's chat LLM (deepseek via `config.yaml`)
is untouched and still works.

Correct flat config for personal_profile:
```json
{
  "llm": {
    "provider": "ollama",
    "config": {
      "model": "llama3.2:3b",
      "ollama_base_url": "http://localhost:11434",
      "temperature": 0.2,
      "max_tokens": 2000
    }
  },
  "embedder": {
    "provider": "ollama",
    "config": {
      "model": "nomic-embed-text",
      "ollama_base_url": "http://localhost:11434",
      "embedding_dims": 768
    }
  },
  "vector_store": {
    "provider": "faiss",
    "config": {
      "path": "C:/Users/khoans/AppData/Local/hermes/profiles/personal_profile/mem0_faiss",
      "embedding_model_dims": 768
    }
  }
}
```

## Verification that PASSED (fresh, post-edit)

Ad-hoc script `hermes-verify-cross-faiss2.py` ran `Memory.from_config(cfg)` +
`m.add()` + `m.search()` for all 3 profiles. Result:
```
[OK] warren-profile: faiss, idx=['mem0.faiss', 'mem0.json']
[OK] stock-profile: faiss, idx=['mem0.faiss', 'mem0.json']
[OK] personal_profile: faiss, idx=['mem0.faiss', 'mem0.json']
=== RESULT: ALL FAISS VERIFIED ===
```
Index files confirmed on disk per profile `mem0_faiss/` dir.

## Stale-reference audit (MANDATORY after swap)

Grep targets + fixes applied this session:
- `stock-profile/SOUL.md` line 95: `| mem0 | Qdrant (vector DB) |` → `| mem0 | FAISS (in-process vector DB) |`
- `personal_profile/SOUL.md` line 40: same → FAISS
- `personal_profile/SOUL.md` §10 MEM0 GATE: "Trước mỗi lần gọi mem0_add" → "dùng `memory` tool ... KHÔNG dùng `mem0_add`"
- `warren-profile/skills/stock/stock-price-sync/scripts/mem0-direct-qdrant.py` → DELETED (Qdrant REST workaround)
- `stock-profile/scripts/mem0-status.sh` → rewrote: reads `vector_store.config.path` (flat), loops 3 profiles, shows faiss_path
- `warren-profile/skills/devops/memory-provider-setup/scripts/mem0-on.sh` → removed Qdrant start block, Ollama-only
- `warren-profile/skills/devops/memory-provider-setup/scripts/mem0-off.sh` → removed Qdrant stop block
- `warren-profile/skills/mem0-search/SKILL.md` → rewrote 336→210 lines, FAISS-only + Qdrant "deprecated" note
- `warren-profile/skills/mem0-search/references/save-workaround.md` → DELETED (all Qdrant)
- `warren-profile/scripts/mem0_search.py` → rewrote: dropped `QDRANT_URL`/`search_qdrant`, added `search_faiss()` via `Memory.from_config()` + `m.search(filters={"user_id":...,"agent_id":"hermes"})`. Verified: `mem0_search.py -p warren "FAISS"` returned 7 results (3 MEMORY.md + 4 FAISS), zero Qdrant calls.
- `references/faiss-backend-swap.md` → KEPT (useful recipe)

## Shell-script verification gotcha

Python `subprocess.run(["bash", ...])` from the hermes venv CANNOT find bash on
Windows (MSYS `/usr/bin/bash` is virtual). Run `bash -n` / `bash script.sh` directly
in the Hermes terminal tool instead. See SKILL.md "Verify shell scripts from Hermes
terminal" pitfall.

## Ollama false-positive log

Ollama `serve` logs `level=INFO ... "waiting for llama-server to become available" status="llm server error"`
during model lazy-load. This is NOT a crash — `curl localhost:11434/api/tags` returns
200 and models list. Do not treat it as Ollama down.
