---
name: telegram-brain-dump-spec
description: "Reference spec for Telegram brain dump system — assumptions, architecture, methodology stack, user preferences from the 2026-06-30 build session."
tags: [telegram, capture, reference, spec]
---

# Telegram Brain Dump Spec — Session 2026-06-30

Reference spec from the session that built `telegram_health_poller.py` with confirmation gate.

## Assumptions (Validated by Warren)

1. **Bot:** `@personal_life_bot` — vừa send vừa poll (getUpdates)
2. **Chat ID:** `2117653672` — lọc message đúng người
3. **Trigger format:** `[capture-sleep]` prefix → xử lý health log
4. **Poll interval:** Every 2 minutes via cron
5. **Confirmation gate:** propose draft → Warren reply "ok" / "edit [text]" / "skip"
6. **State:** `.telegram_pending.json` giữa các poll cycle
7. **Tech:** Python stdlib + Telegram HTTP API, Windows/git-bash

## Architecture

State machine: IDLE → (message có tag) → AWAITING_CONFIRM → "ok"/"edit"/"skip" → COMPLETED (timeout 30ph → IDLE)

## Methodology Stack

Every change follows this order:
1. **Spec-Driven Development** — surface assumptions, write full spec, Warren approves
2. **Planning & Task Breakdown** — dependency graph, vertical slices, acceptance criteria
3. **Incremental Implementation** — one slice at a time, verify each before next
4. **Code Simplification** — preserve behavior, follow conventions, clarity > cleverness
5. **5-Axis Code Review** — Correctness, Readability, Architecture, Security, Performance
6. **Battle Test** — edge cases, corrupt state, network failure, spam
7. **A/B Test** — compare old vs new output format
8. **Debugging & Error Recovery** — Stop-the-Line: preserve → reproduce → localize → fix → guard

## User Preferences

| Preference | Rule |
|------------|------|
| Fresh verification | Every code change re-verified before declaring done |
| Conclusion-first | Present results first, methodology second |
| Incremental delivery | Thin vertical slices, show working result after each |
| Quality gates | Simplicity check + 5-axis review before next slice |
| No silent assumptions | Surface assumptions first, let Warren correct |
