# Interview Session: stock-deploy-capital (2026-06-23)

## Context
Warren needed a single command to synthesize all vault data (pulse + wiki thesis + BCTC + watchlist + holdings) before deploying capital. No existing command did this.

## Interview Flow
- **Question count:** 13 (Q1-Q13)
- **Start confidence:** 65%
- **Stop confidence:** 95% → 100% after Q13
- **Archetypes exhibited:** Numerical Fixer + Batch-Answerer + Confidence Farmer (all 3)

## Key Corrections From Warren

| # | Topic | My guess | Warren correction |
|---|---|---|---|
| 1 | Scope | Holdings only | Both Holdings + Watchlist |
| 2 | Price source | Vault-only | Live fetch, fallback kêu Warren |
| 3 | MOS threshold | >20% | >10% |
| 4 | Intrinsic value | DCF/broker target | P/E 5Y avg × TTM EPS only |
| 5 | Scoring weights | Moat 25, Survival 25 | → 20, 20 (rebalanced Mgmt+Anti 5→10, Catalyst 5→10) |
| 6 | P/B formula | "hợp lý" | P/B ≤ ROE × 0.1 |
| 7 | Valuation in score? | In score | Separate trigger |
| 8 | Anti-thesis | Separate group | Merge with Management |
| 9 | Output format | Data-first | Verdict-first + ma trận 2×2 + pre-flight + action cards |
| 10 | Report format | Markdown | HTML |
| 11 | LLM probability | Not mentioned | Explicitly banned |
| 12 | Save location | Suggestions folder | 040_Deploy_Capital_Report.html |

## What Worked
- **GUESS with numbers** on every question — Warren engaged with and corrected concrete numbers immediately
- **One question at a time** from agent side — even though Warren batch-answered, the single-question framing kept the interview focused
- **Restate at 95%** — Warren confirmed the 5-line restate and added the last refinements
- **Pre-flight gate** — Warren immediately liked the 3-question binary check
- **Quantum-style output** — verdict-first, 2×2 matrix, action cards — all proposed by agent, accepted by Warren

## What Didn't Work
- Asking Q1 without repeating it when Warren skipped it — had to ask twice
- Using abstract terms without numbers ("hợp lý" for P/B) — Warren forced a concrete formula
- Suggesting probability percentages — Warren explicitly banned it

## Template Trigger
When the ask is "tôi muốn tổng hợp toàn bộ thông tin... góc nhìn bao quát nhất trước khi xuống tiền" → use interview-me for `stock-deploy-capital` or similar allocation synthesis command.

## Downstream
- Created: `stock-deploy-capital` skill (SKILL.md + scoring-calibration.md + report-dashboard.html)
- Created: `040_Deploy_Capital_Report.html` vault file
- Patched: `interview-me` skill with 3 user archetypes from this session