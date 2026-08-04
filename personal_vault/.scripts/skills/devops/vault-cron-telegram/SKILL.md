---
name: vault-cron-telegram
description: Telegram delivery patterns for Warren's vault cron scripts — plain-text sending (legacy Markdown `_` pitfall → HTTP 400), never-silent heartbeat rule, and backup-slot dedup so Warren gets at most 1 msg/day. Use when writing or fixing any no_agent cron that sends Telegram (consistency scan, morning brief, receipts, etc.).
version: 1.0.0
author: Hermes
trigger: /vault-cron-telegram, when patching a vault cron that calls send_telegram
category: devops
---

# Vault Cron → Telegram Patterns

Recurring patterns for Warren's vault `no_agent` cron scripts that deliver to
Telegram via `LUsineWorkBot` (chat `2117653672`). Two hard-won rules below.

## Rule 1 — Send PLAIN TEXT, never `parse_mode: Markdown`

The shared `_send_telegram.py` hardcodes `parse_mode: 'Markdown'`. Legacy
Markdown treats `_` as an *italic* delimiter. Ops messages contain file names
with underscores (`OPERATION_INDEX`, `12_Wage`, `14_Menu_GP`, `cron_receipts`)
→ Telegram returns `400 Bad Request: can't parse entities`. **Symptom:**
`TG_RESULT:FAIL|HTTP Error 400: Bad Request` even though a plain message sends.

**Fix:** add a local `send_telegram_plain()` in the cron script (do NOT edit the
shared `_send_telegram.py` — other crons rely on Markdown). Post without
`parse_mode`. Copy-paste implementation + debug recipe in
`references/telegram-markdown-pitfall.md`.

## Rule 2 — Never silent + backup-slot dedup

Warren rule: mọi cron `deliver=all`, "tuyệt đối ko silent". A scan that runs
clean MUST still send a heartbeat (e.g. `✅ Vault Consistency <date>: sạch (0
findings)`) — otherwise Warren can't tell "ran clean" from "missed".

But Warren hates Telegram spam. If you add a **backup cron slot** (e.g. 10:00
primary + 13:00 fallback for machine-off days, same `no_agent` script), dedup
so Warren gets **at most 1 TG msg/day**:
- Store `last_tg_date` in the script's state JSON.
- Skip send if `state["last_tg_date"] == today.isoformat()`.
- Verified: RUN1 `TG_RESULT:OK`, RUN2 `TG_SKIP: already sent today`.

**Prefer this over `deliver: all` on a `no_agent` script** — `deliver: all`
pushes the script's stdout AND the script's own `send_telegram` call = double
msg on findings days. Use `deliver: local` + script-self-send with dedup.

## Rule 3 — Rich HTML reports (PREFERRED for data summaries)

Telegram has **no real tables and no text color**. For data reports (revenue, COL, KPIs) use:
- `<b>...</b>` to bold key numbers (e.g. SYSTEM total, VERIFY PASS).
- `<pre>...</pre>` with manually `ljust()`-aligned columns for store/metric tables (monospace font → columns line up). Use the `aligned_table()` helper in `scripts/send_rich_telegram.py`.
- Emoji (🔝🔻✅🔴) replace red/green color cues.
- Always include a **vs-4-week-average** benchmark line — Warren drives on trajectory, not just W/W%.

HTML `parse_mode` is safe: unlike Markdown, `_` is literal, so file names with underscores (e.g. `01_SSOT_01_Weekly_Revenue_Log`) don't 400. **Never use Markdown `parse_mode` anywhere.**

Working example (sent 2026-07-24, msg_id 1063):
```
✅ <b>W29 REVENUE DONE</b> (4 PowerBI file)
<b>SYSTEM:</b> 684.6M | 2,583 cov | 265k/cover
↳ vs TB4w: <b>+7% rev</b> | +8% cov | -1% avg
<pre>STORE  REV(M)  COV   AVG    W/W     vs TB4w
LU7    243.7   922   264k   +15%   +15%/+16%
LU3    243.0   926   262k   +4%    +9%/+9%
LU5    197.8   735   269k   0%     -3%/-1%</pre>
✅ <b>VERIFY 3 lớp PASS</b> | reconcile ALL CLEAR
```

## When to apply
- Patching `vault_consistency_nightly.py`, `gen_today_and_send.py`,
  `review_telegram_sender.py`, `fill_promo_tracking.py`, or any new vault cron.
- After adding a heartbeat/finding message that includes vault file names.

## Pitfalls
- Stripping `*` (bold) is NOT enough — `_` still breaks Markdown. **Use `parse_mode: HTML` for rich reports:** HTML enables `<b>` bold + `<pre>` aligned tables, and `_` is literal (no italic trap). Only Markdown is banned; HTML is PREFERRED. Reusable sender: `scripts/send_rich_telegram.py` (see Rule 3).
- Don't "fix" the shared `_send_telegram.py` to plain-text globally; it breaks
  other crons that intentionally use Markdown formatting.
- `deliver: all` + script-self-send = duplicate messages. Pick one delivery path.

## References
- `references/telegram-markdown-pitfall.md` — full debug recipe + `send_telegram_plain()` source.
