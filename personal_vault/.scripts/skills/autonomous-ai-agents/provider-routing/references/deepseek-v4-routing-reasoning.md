# DeepSeek V4 Flash vs Pro — Routing Reasoning Data

> Session origin: 2026-06-24. Source: DeepSeek official API docs + WaveSpeed production guide + BentoML complete guide.

## Core Specs

| Metric | V4-Flash | V4-Pro |
|--------|----------|--------|
| Total params | 284B | 1.6T |
| Active params | 13B | 49B |
| Context window | 1M | 1M |
| Max output | 384K | 384K |
| Pricing (input) | ~$0.13/M | ~$1.00/M |
| Pricing (output) | ~$0.33/M | ~$2.50/M |
| **Cost ratio** | **1x** | **~8-10x** |

## Benchmark Gaps (Flash vs Pro)

| Benchmark | Flash | Pro | Gap | Significance |
|-----------|-------|-----|-----|-------------|
| MMLU-Pro | 86.2 | 87.5 | 1.3 | Negligible — general knowledge |
| LiveCodeBench | 91.6 | 93.5 | 1.9 | Negligible — routine coding |
| SWE-Verified | 79.0 | 80.6 | 1.6 | Negligible — software engineering |
| Codeforces | 3,052 | 3,206 | ~150 Elo | Small — competitive programming |
| **SimpleQA-Verified** | **34.1** | **57.9** | **23.8** | **🚩 HUGE — factual recall gap** |
| **Terminal Bench 2.0** | **56.9** | **67.9** | **11.0** | **🚩 LARGE — multi-step tool use** |

## Decision Rules (from benchmark shape)

### Use Flash confidently for:
- General chat, summarization, translation (gap <2 pts)
- Single-pass classification, tagging, extraction (gap invisible)
- Code completion, simple code generation
- Interactive UX where first-token latency matters
- Bounded single-step Q&A (no research/cross-referencing)

### Use Pro for — see trigger conditions in SKILL.md:
- **Factual accuracy** (SimpleQA gap = 23.8 pts): vault queries, P&L numbers, HR data, ops reports
- **Multi-step agentic tasks** (Terminal Bench gap = 11 pts): tool call chains of 3+ steps, sequential reasoning
- **Retry after Flash failure**: Flash failed to produce correct answer → escalate to Pro
- **Long-context comprehension >50K tokens**: Pro maintains coherence better

### Use Flash + Think Max as intermediate:
Flash with `Think Max` mode closely approaches Pro on pure reasoning tasks.
Route to Flash+ThinkMax for medium-complexity reasoning before escalating to Pro.

## Pricing Impact (worst case)

If all requests are Pro: cost = ~9x Flash.
At 10% Pro target: cost = Flash baseline × 1.8x (acceptable for quality gain).
At 15% Pro: cost = Flash baseline × 2.2x.
At 20% Pro: cost = Flash baseline × 2.6x.

## Source Links

- Official DeepSeek V4 release: https://api-docs.deepseek.com/news/news260424
- WaveSpeed production guide: https://wavespeed.ai/blog/posts/deepseek-v4-pro-vs-flash/
- BentoML complete guide: https://www.bentoml.com/blog/the-complete-guide-to-deepseek-models-from-v3-to-r1-and-beyond
