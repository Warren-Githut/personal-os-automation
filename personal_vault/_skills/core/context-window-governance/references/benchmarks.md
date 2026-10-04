# Context-Window Benchmarks — Condensed Bank

> Quoted/condensed from external research. Citations only; not a full mirror.

## Origin of the "150K is where work happens" claim
- **daily.dev essay (2026-07-20)** — NOT a research paper; an essay aggregating practitioner opinions (Matt Pocock, Gergely Orosz, Dex Horthy). Quote: *"1m context windows are a nice gimmick. But you might be better off sticking to only the first 150K tokens."* The 150K figure is the observed point where output quality starts degrading for mainstream models.

## Foundational research (real)
- **Lost in the Middle (Liu et al., Stanford, 2023, arXiv:2307.03172):** LLMs attend best to info at the BEGINNING and END of context; performance degrades significantly for info in the MIDDLE — even for explicitly long-context models. U-shaped attention curve.
- **RULER (Hsieh et al., Nvidia, COLM 2024):** Near-perfect on vanilla needle-in-haystack, but large degradation on aggregation / multi-hop / reasoning-over-context as length grows. "Claimed context size substantially overstates effective capability."

## 2026 production benchmarks (effective ≪ advertised)
- **NIAH-2 + MRCR v2 (digitalapplied.com, 2026):** At 1M tokens, single-needle retrieval: GPT-5.5 96%, Gemini 3 Deep Think 99%, Claude Opus 4.7 89%, DeepSeek V4-Pro 78%. Multi-needle (8 needles) drops sharply: GPT-5.5 74%, Gemini 3 89%, Opus 4.7 56%, V4-Pro 41%.
- **MRCR v2 8-needle (yage.ai, 2026):** Gemini 3.1 Pro 128K: 84.9% → 1M: 26.3%. Claude Opus 4.7 ~76% at 1M (3x gap vs Gemini). Real effective window for non-Gemini frontier models sits in 200–400K band.
- **DeepSeek V4:** advertised 1M window. Reddit/local reports: *"genuinely trash after 256k for coding."* Flash uses a sliding-window branch (window size 128 in paper) → practical effective ~128–256K for warren-profile's `hy3:free`.

## Failure modes when over-stuffed
- Hallucinations increase (confabulation over retrieval)
- Instructions buried mid-prompt get ignored
- Code generation: plausible-but-broken
- Sycophancy ("you're completely right!") = trajectory-poisoned tell → start new session
- Compounding error across repeated auto-summary (dumb zone grows)

## Takeaway for warren-profile
- Stack = DeepSeek V4 Flash (1M advertised, ~128–256K effective) → 150K head = smart zone.
- Don't trust the 1M number. Trust the first 150K + retrieval layer.
- Gemini 3 Deep Think is the only one holding near-perfect through 1M — the sole case to raise threshold to 0.5.
