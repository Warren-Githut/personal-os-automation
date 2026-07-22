---
name: safenet
description: "Pre-output adversarial safe-net for personal-profile — hard gate that routes every plan/parser/script/idea/insight/actionable through the right existing check (review-plan / doubt-driven / verify-parser-output / auto-reviewer), enforces a kill criterion, and emits a 🔰 SAFENET token. For high-stakes outputs, spawns an independent dual-agent critic via delegate_task."
version: 1.1.0
trigger: before any non-trivial output (plan, parser, script, idea, insight, actionable) — unconditional hard gate. Major decisions (🟡+) MUST pass Munger Pre-Mortem Gate.
category: core
---

# /safenet — Pre-Output Adversarial Safe-Net

> Thin router. Does NOT reinvent checks — routes to existing skills + adds the 2 missing pieces: **kill criterion** + **insight/idea/actionable gate**. Hard gate with token (same enforcement model as session-start bootstrap). Built from Greg Isenberg's "AI with a spine" (2026-07-18) + Warren's own gaps (self-audit 2026-07-19). Adapted for personal-profile (health/finance/family/legal domain).

## 🚨 HARD GATE — run BEFORE emitting any non-trivial output

> Structural, non-discretionary. A visible 🔰 SAFENET token proves the gate ran. No token = violation (same as missing boot token).

### 🔰 SAFENET TOKEN (mandatory on every gated output)
```
🔰 SAFENET: ✅ passed [type] — kill-check OK, routed to [gate]
```
or
```
🔰 SAFENET: 🔴 BLOCKED — [reason] (kill criterion hit)
```

## Routing (classify → gate)
> **HARD:** mỗi route PHẢI `skill_view(name)` load skill đích TRƯỚC khi chạy gate. Không load = violation (y lỗi bootstrap 18/07). Router này không tự-chạy gate thay skill.
| Output type | Route to (load trước) | Kill criterion check |
|-------------|----------|----------------------|
| Plan / proposal | `review-plan` (adversarial 4-persona) OR `doubt-driven-development` (decision) | If contradicts vault history → BLOCK |
| Parser / script (production) | `verify-parser-output` + `doubt-driven-development` (code) | If verify gate not PASS → UNTRUSTED, do NOT report |
| Idea / insight / actionable | inline insight-checklist below + cite evidence + apply Personal Min Data Window (A9: ≥2 tuần) | If <2 tuần → STOP + ask Bố |
| **Major output to Warren** (see `auto-reviewer` "DONE" definition A/B/C) | `auto-reviewer` (spawns a SEPARATE reviewer node via `delegate_task`, inherits the chat's free model — NOT hardcoded) — run `verify-parser-output` FIRST if the artifact is numeric | If delivery carries NO `🔍 REVIEWER:` token → violation (same class as missing boot / safenet token) |
| **Major decision (🟡 zone+)** — health intervention, large personal spend, legal move, routine change affecting family | `review-plan` (adversarial) + **Munger Pre-Mortem Gate** (below) — inversion-first: "Điều gì sẽ làm hỏng cái này?" | If pre-mortem NOT done → 🔴 BLOCK. If top risk has no mitigation → flag + ask Bố |

## Insight / Idea / Actionable Checklist (the MISSING gate)
Before shipping any insight/idea/actionable, assert ALL:
- [ ] Data window ≥2 tuần (A9) cho trend — else STOP `[ANCHORS A9]`
- [ ] Every number cites source path + confidence tag `[HIGH]`/`[MOD]`/`[LOW]` — else tag `[UNKNOWN]`
- [ ] Actionable has tradeoff — not "just do X" alone (A4 finance)
- [ ] No contradiction with `personal_vault/` SSOT (PERSONAL_MEMORY.md) — flag if conflict
- [ ] Not re-proposing a Bố-rejected option without new evidence
- [ ] No medical diagnosis (A2) — health advice = source + "see doctor", not prescription

## Kill Criterion (the missing piece from Greg's tweet #5)
Tell Bố to shut it down when ANY:
1. **Data too thin** — <2 tuần cho trend → stop, ask Bố, do NOT proceed.
2. **Unsourced claim** — any conclusion without citeable source → stop, do NOT ship.
3. **Verify failed** — parser/LLM output not through `verify-parser-output` → UNTRUSTED.
4. **Rejected-reopen** — re-proposing a Bố-declined option without new evidence → stop.
5. **Ship-pressure signal** — if Hermes feels pressure to "just ship" over "ship correct" → pause, re-run gate.
6. **Medical overreach** — Hermes chuẩn đoán / kê đơn → BLOCK, redirect "see doctor".

## 🔴 Munger Pre-Mortem Gate — Inversion-First Decision Check

> **"Invert, always invert." — Charlie Munger.** Trước mọi major decision (🟡+), Hermes PHẢI chạy pre-mortem: giả định decision ĐÃ THẤT BẠI sau 30 ngày, rồi truy ngược "tại sao nó chết?"

### Trigger (BẮT BUỘC — không discretionary)
- Health intervention (bắt đầu supplement, thay đổi eating/exercise lớn)
- Large personal spend (chi >10tr VND, ảnh hưởng emergency fund = 0)
- Legal move (kháng cáo, yêu cầu access GG mới)
- Routine change affecting family / work-life

### 6 Inversion Questions (trả lời TỪNG câu, print ra chat)
```
🔴 MUNGER PRE-MORTEM — [tên decision]:
Q1: Nếu 30 ngày sau cái này THẤT BẠI THẢM HẠI — nguyên nhân #1 là gì?
Q2: Ai sẽ phản đối / không cooperate? (bác sĩ, GG, family, chính Warren)
Q3: Assumption nào đang được tin nhất mà CHƯA có data xác nhận?
Q4: Nếu phải kill cái này trong 5 phút — lý do kill là gì?
Q5: Có ai bị thiệt nếu decision này thành hiện thực? (GG, finances)
Q6: Worst-case: thiệt hại tối đa nếu fail hoàn toàn? (sức khoẻ + tiền + thời gian)
```

### Post-Mortem Output (bắt buộc in ra chat)
```
🔰 SAFENET: ✅ passed [pre-mortem] — [N] risks identified
Top killer: [risk #1 — 1 dòng]
Mitigation: [cách giảm risk #1 — 1 dòng, hoặc "CHƯA CÓ — hỏi Bố"]
Confidence: [HIGH/MOD/LOW]
Go/No-Go: [GO nếu top risk có mitigation] / [NO-GO nếu top risk chưa có mitigation + flag Bố]
```

### Munger's Checklist (mental models — chọn ≥2 áp dụng)
| Model | Câu hỏi áp dụng |
|-------|----------------|
| **Inversion** | "Muốn fail cái này — làm thế nào?" → làm ngược lại |
| **Margin of Safety** | "Worst-case thiệt hại có chịu được không? Cần buffer bao nhiêu?" (emergency fund = 0!) |
| **Circle of Competence** | "Mình có thực sự hiểu y tế/luật này? Hay đang đoán?" |
| **Incentives** | "Ai được lợi / ai bị thiệt? Incentive của họ là gì?" |
| **Second-Order Effects** | "Hệ quả tiếp theo? (vd: supplement → tương tác thuốc → side effect)" |
| **Confirmation Bias** | "Mình đang tìm evidence ủng hộ hay thực sự test?" |

### Kill Criterion Integration
Nếu pre-mortem phát hiện BẤT KỲ điều nào sau đây → **🔴 NO-GO, flag Bố ngay:**
1. Top risk không có mitigation strategy
2. Worst-case thiệt hại > buffer chịu được (emergency fund = 0 → cực thận trọng)
3. Decision dựa trên assumption chưa verified (confidence = LOW/UNKNOWN)
4. Incentive misalignment — người thực thi có lý do để fail

### Token (mandatory trên mọi gated output)
```
🔰 SAFENET: ✅ passed [pre-mortem] — 3 risks, top killer: [X], mitigated by [Y], GO
```
hoặc
```
🔰 SAFENET: 🔴 BLOCKED [pre-mortem] — top risk [X] no mitigation, flagging Bố
```
(same format as §🔰 SAFENET TOKEN above)

## D. Independent Dual-Agent Critic (high-stakes ONLY)
Spawn via `delegate_task` ONLY when output is high-stakes:
- Parser touching production / real vault data
- Plan with financial / health impact
- Irreversible op (delete / rename / data removal)

Critic subagent gets ARTIFACT + CONTRACT (NOT Hermes's conclusion), adversarial prompt from `doubt-driven-development` Step 3. Reconcile findings against artifact — do NOT rubber-stamp (fresh reviewer can be wrong from lack of context).

## Pitfalls
- **Doubt theater**: self-review of own output = shared blind spot. Use D (independent) for high-stakes; routing gate suffices for low-stakes.
- **Token without gate**: never emit ✅ without actually running the routed check.
- **Over-gating**: low-stakes (lookup, summarize) → skip heavy gate, but still emit `🔰 SAFENET: ✅ passed [lookup]` (cheap, proves discipline).
- **Silent skip**: if gate would block, say 🔴 + reason. Never hide.
- **Lean**: xem nguyên tắc router ở intro — không duplicate logic của skill được route.
