---
name: telegram-watcher-safety
description: Build safe Telegram watchers no 409 no git corruption.
tags: [telegram, watcher, cron, no-agent, git-safety, 409, warren]
---

# Telegram Watcher Safety (Warren vault)

Class-level skill for building **no_agent Telegram-triggered commit watchers**
that are both (a) free of the 409 double-consumer conflict and (b) safe against
git working-tree corruption.

## When to use
- Building a cron that waits for a Warren Telegram approval (e.g. "ok 09") then
  commits/pushes vault files.
- Any watcher that would otherwise `getUpdates`-poll the same bot token the live
  `LUsineWorkBot` already holds.
- Any no_agent script that does git operations in the Warren vault repo.

## Core pattern: QUEUE-FILE handoff (kills 409)
Telegram allows ONLY ONE long-poll connection per token. The live bot
(`LUsineWorkBot`, `launch_bot.py` → `lusine_ops/telegram_bot.py`) holds it.
A second `getUpdates` poller gets **409 Conflict**.

**Do NOT poll Telegram from the watcher. Instead:**
1. Add a tiny handler in the LIVE bot: on exact trigger text (e.g. `"ok 09"`),
   append `{user_id, text, ts}` to a JSON queue file
   (`vault/.scripts/.hourly_approval_queue.json`). Reply "✅ nhận được" in-chat.
2. The no_agent watcher reads that queue file, processes pending entries, then
   clears the file. It NEVER calls `getUpdates`.

This eliminates 409 entirely (watcher touches no Telegram inbound).

## Common mistakes (pitfalls)
- **Mistake:** watcher polls `getUpdates` on the same token as the live bot.
  → 409 every run. Fix: queue-file handoff above.
- **Mistake:** watcher does `git pull --rebase --autostash origin HEAD` on push
  rejection. → checks out remote tip (may be OLD commit), untracks whole
  `vault/`, corrupts working tree. `rebase --abort` then re-applies autostash and
  jumps HEAD to a stale/test commit.
  → Fix: scoped commit only, no auto-rebase (see git rules below).
- **Mistake:** E2E test harness does `git reset --hard` + `rm` source files.
  → deletes the very script under test. → Fix: use UNIQUE temp filenames per
  run; cleanup only the temp commit (`reset --soft <before>`) + temp file; never
  `rm` the production source.

## Git safety rules for no_agent watchers (Warren vault)
- NEVER run `git pull --rebase` / `git reset --hard` in a cron script.
- Use scoped: `git add <explicit 2 files>` → `git commit -m "..."` →
  `git push origin HEAD`.
- If push is rejected (non-fast-forward / Bố pushed elsewhere): DO NOT
  auto-rebase. Call `_tg_red("PUSH REJECTED: ...")` + raise. Warren resolves
  manually. (Auto-rebase can corrupt the working tree — observed 2026-07-27.)
- Only `git push --force-with-lease origin master` from a FOREGROUND session,
  and ONLY after confirming the remote tip is your own E2E trash, never Bố's work.
- Guard against double-commit: persist `last_committed_week` in a state file;
  skip if current ISO week already committed (avoids 20x spam on a 30-min cron).

## Warren 7-point compliance (for approval watchers)
- Failed → Telegram 🔴 short, never silent (point 1).
- Success → Telegram ✅ with short analysis (point 2).
- Trigger must be UNIQUE per cron (e.g. "ok 09" vs col "ok" vs review) to avoid
  clash when many T2 crons run (point 7).
- Every Bố reply → ack "nhận được"/"failed" immediately, never silent (point 6).
- Mojibake gate: ASCII in prints (no_agent); TG messages plain-text sender
  (filenames have `_` → no parse_mode).

## Token / offset hygiene
- Watcher offset file must be PRIVATE (not shared with `col_telegram_intake`
  `.col_telegram_offset.json`) to avoid cross-cron race if Bố runs manually.
- Queue file is the single source of truth for approval; no TG offset needed.

## Reference
- `references/recovery_git_corruption.md` — exact recovery recipe when a
  rebase/reset corrupts the working tree (reflog → backup → reset --hard →
  force-with-lease → restore).
