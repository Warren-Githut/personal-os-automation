---
name: ab-test
description: "A/B comparison testing for vault/LLM system. Compares 2 variants (parser, prompt template, vault structure) and recommends the winner."
category: testing
tags: [vault, testing, comparison, ab-test]
related_skills: [battle-test, shipping-and-launch, incremental-implementation]
---

# ab-test

## Overview

A/B test for vault ecosystem decisions. Compares 2 variants and recommends:
- **Winner:** A / B / Both bad (need C) / Equal
- **Score diff:** quantitative comparison
- **Recommendation:** actionable next step

- **Output:** PASS + winner recommendation (full JSON details)
- **No auto-run:** manual trigger only

> **See also:** `references/comparison-patterns.md` — A/B comparison methodology, winner logic.

## Commands

```
ab-test                         → interactive: choose type
ab-test --type parser           → parser A (strict SOP) vs B (lenient)
ab-test --type prompt           → prompt template A (concise) vs B (detailed)
ab-test --type vault            → vault structure tag-heavy vs folder-heavy analysis
```
> Note: `ab_test_runner.py` supports `--type {parser,prompt,vault}` only. `--type memory` and `--type model` are documented methodologies (references/memory-provider-comparison.md, references/methodology.md) run manually — they have no script backing and will argparse-error if passed to the runner.

---

## Context Wrapper

### Environment Context

- OS: Windows 10 — git-bash (MSYS), POSIX shell
- Warren OS vault: /c/Users/khoans/Documents/Warren_OS_Local/vault
- Personal OS vault: /c/Users/khoans/Documents/[personal_vault_path]
- Hermes profiles: warren-profile (ops), personal_profile (investing/finance)
- Workspace constraint: CẢ 2 vault đều OUTSIDE Hermes workspace boundary → File ops via terminal/execute_code, không direct write_file
- File encoding: Windows CP1252 ↔ UTF-8 issues possible in raw files

### Severity Scale (A/B test output)

| Level | Meaning |
|-------|---------|
| A wins | Variant A significantly outperforms B |
| B wins | Variant B significantly outperforms A |
| EQUAL | No meaningful difference |
| DEPENDS | Trade-off requires context-specific decision |
| BOTH_BAD | Neither variant meets threshold — need variant C |

---

## Prompt Core

```
Bạn là Vault Full-Stack Adversarial Tester — chuyên gia A/B test cho Obsidian Second Brain system.

Hôm nay bạn cần so sánh 2 biến thể (parser, prompt template, hoặc vault structure) của cùng một hệ thống.

Quy trình:
1. Hiểu rõ 2 biến thể A và B (đặc điểm, cách hoạt động, trade-offs)
2. Thiết kế test case cho từng biến thể
3. Chạy comparison với dữ liệu thật từ vault
4. Xác định winner dựa trên metrics:
   - Parser: parse speed, error rate, metadata extraction quality
   - Prompt: output quality, completeness, hallucination rate
   - Vault structure: findability, cognitive load, query speed
5. Report kết luận: Winner + Score Diff + Recommendation

Giọng điệu: Thẳng thắn, data-driven. Steel-man cả 2 variants trước khi critique.
```

## Methodology
See `references/methodology.md` for: parser A/B comparison strategy, prompt template scoring rubric, vault structure classification, report format, and run timing.

### Windows encoding A/B test
See `references/windows-encoding-ab-test.md` for: comparing UTF-8 vs cp1252 stdout encoding variants on Windows, subprocess simulation of cron no_agent delivery path, interpretation matrix, and prevention.

### Memory Provider Comparison (--type memory)
Use when evaluating vector-search (Mem0, Qdrant, etc.) vs keyword-search (SQLite FTS5, built-in) memory systems.

**Test design:**
1. Store 5+ facts using exact keywords
2. Query with **different wording** than stored keywords (e.g. stored "cafe den" → query "do uong yeu thich")
3. Measure: semantic hit rate, avg latency, auto-extraction quality

**Scoring rubric:**
| Metric | Weight | Mem0 target | Built-in target |
|--------|--------|-------------|-----------------|
| Semantic recall (different wording) | 40% | ≥80% | ≤20% (FTS5 fails) |
| Exact keyword recall | 20% | 100% | 100% |
| Avg latency | 20% | ≤500ms | ≤10ms |
| Auto fact extraction | 20% | YES | NO (bonus) |

**Pitfall:** Qdrant local mode on Windows locks `~/.mem0/migrations_qdrant` via portalocker/msvcrt — cannot create & close multiple Memory instances in the same Python process. Workaround: use `subprocess.run()` per test, or run one Memory per process. See `references/memory-provider-comparison.md` for full reproduction.

**Winner logic:** Mem0 wins on semantic recall (vector search understands meaning). Built-in only wins on latency (no network/embedding call). If project needs "find X even when asked differently," Mem0 is the clear choice.

### Model Comparison (--type model)
Use when comparing two LLM models (e.g. DeepSeek V4 Flash vs Pro) to decide on cost/quality routing.

**Test design:**
1. Pick 3-5 representative tasks spanning simple→complex
2. Send exact same prompt to both models (same system prompt, same max_tokens)
3. Measure: latency, token usage, response quality (content length, reasoning depth), cost

**Scoring rubric:**
| Metric | How to measure |
|--------|---------------|
| Latency | `time.time()` before/after API call |
| Response completeness | Content length in chars (empty = reasoning consumed all budget) |
| Reasoning depth | `reasoning_content` length (longer ≠ better, but signals model effort) |
| Token efficiency | Total tokens vs useful content ratio |
| Cost | Use official API pricing × token count |

**Pitfalls (from this session):**
- `max_tokens` can be fully consumed by reasoning tokens (`reasoning_content`), leaving empty `content`. Use `max_tokens=500+` or separate reasoning + output budgets.
- Cheaper models (Flash) sometimes produce MORE useful output on simple tasks because they don't over-think. Pro is not always better.
- The config.yaml provider `base_url` may point to a dead local proxy. Always test against the real API endpoint.
- API keys in `.env` files use `KEY=***...***` masked format. Use `grep ^KEY= .env | cut -d= -f2` to extract the real key.

**Winner logic:** If cheap model produces equivalent or better output on a given task class, it wins for that class. Router should map task type → model, not use a single model for everything.

## Usage

### Manual trigger (recommended when evaluating change)
```
ab-test                         → full A/B suite
ab-test --type parser           → parser variant comparison
ab-test --type prompt           → prompt template comparison
ab-test --type vault            → vault structure comparison
```

### Response format
- **Winner + Reason:** clear verdict
- **A vs B metrics:** quantitative comparison
- **Delta:** difference in key metrics
- **Recommendation:** actionable next step

---

## Adversarial Battle Test (from `battle-test`, merged 2026-07-22)

> Vault system adversarial battle testing — pre-ship gate for vault/LLM ecosystem. Stress tests parsers, scripts, vault structure, skills, and end-to-end workflows.

### Testing Approach: pytest vs Vanilla Python
| Dùng vanilla Python khi | Dùng pytest khi |
|---|---|
| Vault structure check (YAML, links, encoding) | Hàm tính toán (revenue, KPI, parser logic) |
| End-to-end integration test | Unit test function riêng lẻ, cần assert chính xác |
| Cần subprocess isolation (Qdrant lock) | Cần parametrize (1 hàm test nhiều input) |
| Script đơn giản, 1 file | Regression test — chạy lại định kỳ |

`python3` (3.14) có pytest 9.1.0 sẵn. Không overengineer.

### Commands
```
battle-test                  → run full suite
battle-test --scope parser   → parser-only
battle-test --scope scripts  → scripts-only
battle-test --scope vault    → vault structure only
battle-test --scope skills   → skill integrity only
```
> Note: `--scope memory` NOT supported (use `ab-test --type memory`).

### Severity Scale
| Level | Meaning | Action |
|-------|---------|--------|
| Critical | Block ship — system integrity compromised | Notify Warren immediately, halt deploy |
| Major | Significant degradation — workaround exists | Notify Warren, non-blocking |
| Minor | Cosmetic / non-functional | Pass only |
| Info | Observation, not a bug | Pass only |

### Coverage Metrics (all reports)
| Metric | Threshold |
|--------|-----------|
| YAML frontmatter valid % | ≥ 95% |
| Link integrity % | ≥ 90% |
| Script parse success % | ≥ 95% |
| Execution time | < 180s |
| Overall score | ≥ 90% |

### Vault-Specific Failure Modes
1. YAML frontmatter parse error
2. File path encoding (Windows `\` vs `/`, Unicode filenames)
3. Broken Obsidian links
4. Semantic drift (note contradicts newer SOPs)
5. Metadata inconsistency
6. Malformed Dataview queries
7. Cross-profile reference without import guard
8. Script import error (sys.path, missing deps) — Windows gotcha: git-bash `$HOME` expands POSIX but python3 is Windows → sys.path no-op
9. Qdrant local lock conflict — subprocess isolation per test

### Prompt Core
```
Bạn là Vault Full-Stack Adversarial Tester — chuyên gia kiểm thử khắc nghiệt.
Test: Vault Structure / Parsers / Scripts / Custom Skills / End-to-End Workflow.
Principles: Adversarial · End-to-End & Multi-Layer · Metric-Driven · Coverage (happy/edge/stress/regression/security).
Steel-man thiết kế hiện tại trước khi critique.
```
