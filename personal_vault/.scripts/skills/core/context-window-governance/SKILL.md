---
name: context-window-governance
description: "Manage Hermes context-window quality for warren-profile — configure compression (threshold/protect_last_n via `hermes config set`), understand effective-vs-advertised context, the fixed-threshold rule, and the retrieval-layer principle for keeping context <150K with quality. Use when discussing long-session quality, model upgrades, or 'why is Hermes degrading'."
version: 1.0.0
author: Hermes
trigger: "/context-window-governance (when configuring compression, evaluating a model upgrade, or diagnosing long-session quality loss)"
category: core
---

# /context-window-governance — Context Quality for warren-profile

> **Why this exists:** 1M context windows are a marketing ceiling. Effective context (where retrieval/reasoning hold up) is far smaller. For warren-profile (DeepSeek V4 Flash: advertised 1M window, effective ~128–256K), the practical "smart zone" is the first ~150K. This skill captures HOW to keep Hermes sharp — config + principle — not just a memory note.

## When to use
- Warren asks about long-session quality, "why is Hermes forgetting/confabulating", or "should we upgrade to a bigger model".
- Configuring or re-configuring context compression.
- Diagnosing "trajectory-poisoned" sessions (sycophantic "you're right!", ignored mid-prompt instructions, plausible-but-broken output).

## Configure compression (commands)
config.yaml is write-protected — use `hermes config set`, NOT hand-edit/patch.
```
hermes config set compression.threshold 0.20
hermes config set compression.protect_last_n 30
```
- **Restart required:** config is read once at startup. Changes apply ONLY after `/reset` or a new session. The session where you ran the command still uses the old value — always tell Warren to restart.
- Defaults: `threshold: 0.50` (fires at 50% of window), `protect_last_n: 20`.
- Dual system: Gateway hygiene @85% of window + Agent `ContextCompressor` @threshold. Keeps `protect_last_n` recent messages + 3 head messages uncompressed. Target tail = threshold × `target_ratio` (default 0.20–0.30).

## THE FIXED-THRESHOLD RULE (don't hardcode per model)
- **Keep `threshold=0.20` fixed** for warren-profile. DeepSeek V4 Flash advertised 1M but effective ~128–256K → 0.20 fires at ~200K, safely inside the smart zone.
- If a smaller-window model is used (e.g. real 256K window), 0.20 = ~51K — still SAFE (early compression beats late). Do NOT bump threshold per model.
- **ONLY raise to 0.5** if Warren switches to Gemini 3 Deep Think (holds ~99% retrieval through the full 1M window).
- Consequence: never re-tune threshold on every model swap. % of *advertised* window is the stable anchor because effective window is always << advertised for mainstream models.

## THE REAL FIX: retrieval layer, not just compression
Compression is DEFENSIVE but LOSSY — auto-summary drops info; repeated compression = compounding error (worsens "lost in the middle").
- **Keep live context small via retrieval, not via dumping + summarizing.** The retrieval layer = vault indexes (`00_WIKI_INDEX`, `00_OPERATION_INDEX`), `WARREN_MEMORY`/`ANCHORS`, skills, `session_search`.
- Practical for Warren (non-IT): focus 1 task per chat; don't say "read the whole vault"; trust summarized answers that cite sources. That IS using the retrieval layer.

## Pitfalls
- **Hand-editing config.yaml** → rejected (write-protected) or UTF-8/BOM issues. Use `hermes config set`.
- **Forgetting restart** → thinking config applied when it didn't. Always note "restart to apply".
- **Trusting 1M** → vendor single-needle benchmarks hide multi-needle degradation. See `references/benchmarks.md`.
- **Bumping threshold per model** → unnecessary churn; 0.20 is safe across mainstream models.
- **Confusing with `compress-memory` skill** → different domain: `compress-memory` = vault WARREN_MEMORY distillation; this skill = LLM runtime context window. Same word "compress", unrelated.

## references/
- `references/benchmarks.md` — condensed research: Lost in the Middle (2023), RULER (2024), NIAH-2/MRCR v2 2026 grid, daily.dev essay origin. Citations only, no full upstream mirror.
