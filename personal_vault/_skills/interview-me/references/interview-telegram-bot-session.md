# Interview: Telegram Bot Feature

## Session Summary

**User Goal:** "Non-friction, chạy ngầm 24/7" Telegram bot for case management

**What User Actually Wanted (vs. What Was Asked):**
| Asked | Actually Wanted |
|-------|-----------------|
| "cài NSSM service" | "chạy ngầm 24/7, không đòi hỏi password, không cần config phức tạp" |
| "cài cronjob" | "ko phù hợp polling bot" |
| "webhook" | "quá phức tạp, cần HTTPS, VPS, không non-IT" |

## Hypothesis Evolution

| Round | Hypothesis | Confidence | Missing Info |
|-------|------------|------------|--------------|
| 1 | "Want NSSM service with 3 profiles" | 65% | Vault sharing, skill distribution, auth |
| 2 | "Want shared vault + optional calendar + Telegram" | 75% | Auth method, setup complexity |
| 3 | "Want zero-friction: .bat in Startup > NSSM" | 95% | None - confirmed |

## Key Insights

### 1. "Apply cho cả 3 profile" = System Thinker
User meant: **single source of truth (vault), 3 profiles consume it**. Not "duplicate code 3 times".

### 2. "Non-friction cho Warren" = Zero Config
- No NSSM setup (requires admin, password, service management)
- No `.env` editing (auto-detect token)
- Click `.bat` → works. That's it.

### 3. "System thinker" = Single Source of Truth
- Vault = truth (`vault/scripts/`)
- 3 profiles = thin wrappers importing from vault
- Change in vault → instant update in all profiles

### 3. "Fix parser như system thinker" = Root Cause Fix
Not "patch symptom" (replace each bad char), but "fix root" (unicodedata NFD normalization).

## Missed Signals (What I Should Have Caught Earlier)

| Signal | Missed? | What It Meant |
|----------|---------|---------------|
| "cronjob" then "webhook" | Yes | User exploring, not committed |
| "tôi mới nhập rồi đó" (impatient) | Yes | User already did the work, just need me to verify |
| "non-friction cho dân non-it" | Partially | Ignored NSSM complexity initially |
| "bạn tự fix parser" | Yes | User wanted me to own the fix completely |

## What Worked Well

1. **Interview → Spec → Plan → Task → Implement** workflow prevented scope creep
2. **Spec first** caught Vietnamese slug issue early (would have been bug in prod)
3. **TDD** caught regressions when fixing slug + optional calendar
3. **Vertical slices** (NL commands → Telegram → Service) kept focus
4. **Single source of truth** principle guided all architecture decisions

## Anti-Patterns to Avoid Next Time

| Anti-Pattern | What Happened | Better |
|--------------|---------------|--------|
| Starting with NSSM | 30 min debugging PATH/permissions | Start simple (.bat), escalate only if needed |
| Multiple .env files | Confusion which one loads | Single .env in secure location, loaded by .bat |
| NSSM before testing bot | 1 hour debugging "Access denied" | Test in .bat first, then NSSM if needed |
| Assuming user wants "best practice" | User wanted "click 2 lần xong" | Ask: "what's your actual workflow?" |

## What to Ask Next Time

1. "Show me your current workflow" (before proposing solution)
2. "What's the simplest thing that could work?" (before proposing best practice)
3. "What's your pain point with current approach?" (before adding features)
4. "If this breaks at 3am, how do you want to be woken up?" (for monitoring/alerting)

## Session Metrics

| Metric | Value |
|--------|-------|
| Rounds of interview | 4 |
| Confidence at stop | 95% |
| Signals caught late | 3 |
| Corrections made | 2 (NSSM → .bat, parser root cause) |
| Time to alignment | ~45 min |