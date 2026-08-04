---
name: telegram-bot-polling
description: "Use when building Telegram poll — cron, watchdog, gate, 409."
version: 1.0.0
author: Hermes
tags: [telegram, polling, watchdog, automation]
---

# Telegram Bot Polling — Hermes Desktop Patterns

Patterns for Telegram bot polling on Hermes Desktop (no webhook).

## Two Polling Modes

| Mode | Real-time? | Durable? |
|------|-----------|----------|
| **Cron Poller** (`*/N * * * *`) | ❌ | ✅ |
| **Long-poll Watchdog** (60s timeout) | ✅ ~2-3s | ❌ |

Best practice: Run BOTH.

## Confirmation Gate — Two Modes

**Mode 1 — Reply to Draft:** User replies to bot's draft → reply_to_message_id match.

**Mode 2 — Bare ok/skip:** User types ok/skip as standalone message. Check pending exists + no reply_to.

## 409 Conflict

Only ONE getUpdates at a time. Watchdog: retry with backoff. Cron: exit silently, retry next cycle.

## Pitfalls

- **409**: Most common failure. Always handle with retry.
- **Bare ok**: If Mode 2 not implemented, user's ok is silently ignored.
- **Offset rollback**: Telegram clears old updates from cache. Never roll back.
- **State file**: Write atomically (.tmp → rename), auto-recover on parse failure.
- **Dedup**: In-memory set per session + vault date check.
