# Mem0 Weekly Cleanup — Cron Pattern

> Implemented 2026-06-26 for Warren's 3-profile setup (warren, personal, stock).
> Updated 2026-06-28: removed curl Telegram from prompts — blocked by scanner.

Each profile has isolated Mem0 via different `user_id` values in `mem0.json`.

## Architecture

3 cron jobs, 1 per profile, staggered 5 minutes apart on Sunday morning:

| Profile | Cron ID | Schedule | Job Name |
|---------|---------|----------|----------|
| warren | `92547e08c21b` | `0 9 * * 0` (09:00) | mem0-cleanup-warren |
| personal | `5d91facfda39` | `5 9 * * 0` (09:05) | mem0-cleanup-personal |
| stock | `b550fb037fec` | `10 9 * * 0` (09:10) | mem0-cleanup-stock |

## Cron Job Spec

```yaml
no_agent: false               # LLM-driven để format report
attach_to_session: true       # Continuable session
deliver: origin               # Desktop chat; auto-fallback Telegram when origin unavailable
model: deepseek-v4-flash      # Flash đủ cho task nhẹ
workdir: <vault-root>         # Required for vault file writes
```

**Delivery:** `deliver: origin` auto-fallbacks to Telegram when origin (TUI) is unavailable — no curl needed. The cron scheduler already delivers job output to the home channel (`telegram:2117653672`) as confirmed in logs.

**⚠️ DO NOT put curl/sendMessage in LLM-driven prompts.** The cron injection scanner (`exfil_curl_url`) blocks any prompt containing `curl -X POST "https://api.telegram.org/bot$TOKEN/sendMessage"`. Instead, rely on the built-in `deliver` mechanism. If you need Telegram delivery, set `deliver: telegram:<chat_id>` or `deliver: origin` (auto-fallback).

## Prompt Template

Key sections every prompt needs:

1. **Scan:** `mem0_list(page_size=100)`, apply MEM0 GATE criteria
2. **Report format:** Per-profile header, numbered list, artifact/duplicate/stale tags
3. **Reply handling:** Save pending list to `vault/_inbox/mem0_pending_cleanup.json`; process "ok"/"keep N" on next agent turn
4. **Silent when clean:** If 0 noise → "✅ [PROFILE] Mem0 sạch — N memories" (delete pending file if exists)
5. **Reminder:** If no reply after 24h → 1 reminder only, no spam

**No Telegram curl in prompt** — delivery is handled by the cron scheduler's `deliver` mechanism.

## Noise Detection Criteria

| # | Criterion | Pattern |
|---|-----------|---------|
| 1 | Artifact | File paths (.py, .md, /), cron IDs (12-char hex), "script", "bug", "test", "đã fix", config details |
| 2 | Stale | Not a preference/decision/config. Temporary data (prices, dates, "hôm nay"). Vague questions |
| 3 | Duplicate | Content >70% overlap with another memory → keep shorter, flag longer |

## Limitation: Reply Handling

`attach_to_session=true` does NOT keep the cron session alive to wait for user reply. The agent produces output and exits. Workaround:

1. Cron saves pending cleanup list to vault JSON file
2. User replies "ok" in main desktop chat
3. Main Hermes agent reads the file, calls `mem0_delete` for flagged items
4. Confirms deletion results

## Cross-Profile Cron Creation

Hermes `cronjob` tool lacks a `--profile` flag. To create crons in non-active profiles:
- Directly edit `~/.hermes/profiles/<name>/cron/jobs.json`
- Generate 12-char hex ID (md5 hash of name, truncated)
- Follow the exact JSON schema from existing jobs
- Restart gateway or scheduler to pick up new jobs

## Related Files

- `references/mem0-cleanup-workflow.md` — Manual cleanup recipe (37→6 + 13→5 sessions)
- `references/cross-profile-mem0-scanning.md` — Python multi-config scanning pattern

## Code Review Findings

| Date | Issue | Fix |
|------|-------|-----|
| 2026-06-26 | Token syntax `%TELEGRAM_BOT_TOKEN%` (Windows) in warren prompt — bash terminal needs `$TELEGRAM_BOT_TOKEN` | Changed to `$VAR` syntax + added explicit curl command for personal/stock prompts |
| 2026-06-26 | Stock pending file named `mem0_pending_stock_cleanup.json` — inconsistent with warren/personal | Unified to `mem0_pending_cleanup.json` across all 3 |
| 2026-06-26 | Personal + stock missing cleanup line in 0-noise case | Added `(xóa pending file nếu có)` to both prompts |
| **2026-06-28** | **curl/sendMessage in LLM-driven prompts blocked by `exfil_curl_url` scanner** | **Removed all curl commands from prompts. Rely on `deliver` mechanism. Added `workdir` to cron job config.** |
