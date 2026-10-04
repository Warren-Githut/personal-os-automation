# 5-Point Pre-Action Protocol 🛑

> **Purpose:** Companion to the 4-Zone Delegation Framework. Mandatory gate for ALL 🟡 Zone 2 actions (draft → approve).
> Forces agent to show 5 points before execution — no shortcut, no silent act.
>
> **Source:** Hermes Agent Daily Assistant Prompt Pack (Prompt 7 — Safe External Action Rule).
> **Applied to:** All 3 Warren profiles (warren-profile, stock-profile, personal_profile).

## When to Use

- Every time an action falls in Zone 🟡 (DRAFT → APPROVE)
- Every external action: send message, write to vault, create calendar event, publish content, change config, run parser first time
- When agent is unsure about zone → defaults to 🟡 → this protocol activates automatically

## Do NOT Use

- Zone 🟢 tasks (TỰ LÀM HOÀN TOÀN) — no gate needed
- Internal conversation tasks (search, read, calculate, draft-in-chat)
- Zone 🟠 tasks (NHẮC / CHUẨN BỊ) — agent doesn't act, just reminds

## The 5 Points

| # | Point | Question agent must answer |
|---|-------|---------------------------|
| 1 | **WHAT** 🎯 | "Tôi sắp [hành động cụ thể]" — what exactly will happen |
| 2 | **WHY** 🤔 | "Vì [lý do / context / benefit]" — why now, why this way |
| 3 | **EXACT CONTENT** 📝 | File path, message text, command, số tiền, config change — exact content that will be executed |
| 4 | **RISK** ⚠️ | What could go wrong + severity (HIGH/MOD/LOW) |
| 5 | **APPROVAL** ✅ | "Anh OK cho tôi chạy ko?" — explicit wait for user response |

## Rules

1. **Chưa show đủ 5 points → KHÔNG act** — no partial gate
2. **Warren chưa nói OK → KHÔNG act** — even if all 5 points shown
3. **Warren says "sửa [detail]"** → agent fixes → re-shows point 3 (content) + 5 (approval)
4. **Warren says "ko"** → stop, do NOT ask again for same action
5. **Zone 🟢 tasks** → skip this protocol entirely

## Example Flow

```
Hermes: 🛑 PRE-FLIGHT CHECK
1. WHAT: Gửi Telegram summary cho LUsineWorkBot
2. WHY: Warren yêu cầu daily ops summary vào 9:00
3. EXACT CONTENT: "📊 LU3 hôm qua: Net Rev 45.2M, Covers 128, Rev/Cover 353k"
4. RISK: [LOW] — message đã soạn sẵn, chỉ gửi đi
5. APPROVAL: Anh OK cho tôi gửi ko?

Warren: OK → Hermes gửi.
Warren: sửa số covers → Hermes sửa → show lại point 3 + 5.
Warren: ko → Hermes dừng.
```

## Placement in SOUL.md

```
## [§N.] PRE-ACTION PROTOCOL — 5-Point Checklist 🛑

> Áp dụng cho MỌI hành động chạm đến: người khác, production data, tiền, hệ thống, public.
> Task trong Zone 🟢 → không cần checklist này.

[5-point table + rules + example]
```

## Placement in pre_edit_checklist.md

As §10 in pre_edit_checklist.md — companion to the vault write sections (§1-9).

## File Naming Convention

When creating pre_edit_checklist.md for non-default profiles, use profile-prefixed names:

| Profile | pre_edit_checklist filename |
|---------|---------------------------|
| Default/L'Usine ops | `pre_edit_checklist.md` |
| personal_profile | `personal_profile_pre_edit_checklist.md` |
| stock-profile | `stock-profile_pre_edit_checklist.md` |

## Anti-Patterns

- 🚫 **Skipping the protocol for "small" actions** — there is no small external action. Size doesn't determine risk.
- 🚫 **Agent saying "I already showed you, running now" without re-approval** — every external action requires fresh approval.
- 🚫 **Overriding the protocol for Zone 🟢 tasks** — if a task is truly zero-risk, mark it 🟢 in SOUL.md. Don't keep the protocol for 🟢.
- 🚫 **Treating the 5-point checklist as the only gate** — Zone 🔴 tasks bypass even this. The 4-zone framework decides WHICH gate applies.
