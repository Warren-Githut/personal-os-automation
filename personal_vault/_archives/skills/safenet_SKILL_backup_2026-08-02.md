---
name: safenet
description: "Pre-output adversarial safe-net for stock-profile — hard gate that routes every plan/parser/script/idea/insight/actionable through the right existing check (review-plan / doubt-driven / verify-parser-output / auto-reviewer), enforces a kill criterion, and emits a 🔰 SAFENET token. For high-stakes outputs, spawns an independent dual-agent critic via delegate_task."
version: 1.2.0
trigger: before any non-trivial output (plan, parser, script, idea, insight, actionable) — unconditional hard gate. Major decisions (🟡+) MUST pass Munger Pre-Mortem Gate.
category: core
---

# /safenet — Pre-Output Adversarial Safe-Net

> Thin router. Does NOT reinvent checks — routes to existing skills + adds the 2 missing pieces: **kill criterion** + **insight/idea/actionable gate**. Hard gate with token (same enforcement model as session-start bootstrap). Built from Greg Isenberg's "AI with a spine" (2026-07-18) + Warren's own gaps (self-audit 2026-07-19).

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
| Idea / insight / actionable | inline insight-checklist below + cite evidence + apply Stock Min Data Window (A7: ≥4 quý sạch) | If <4 quý → STOP + ask Bố |
| **Major output to Warren** (see `auto-reviewer` "DONE" definition A/B/C) | `auto-reviewer` (spawns a SEPARATE reviewer node via `delegate_task`, inherits the chat's free model — NOT hardcoded) — run `verify-parser-output` FIRST if the artifact is numeric | If delivery carries NO `🔍 REVIEWER:` token → violation (same class as missing boot / safenet token) |
| **Silent-failure hunting / false-green check** | `audit-automation` (failure-signal pattern) — see §F | If audit finds silent cron → 🔴 escalate, do NOT let Bố discover from customer complaint |
| **Warren analysis/report (ANY — kể cả zone 🟢)** | **FORCED** `qa-gate` → (if PASS + zone 🟡/🔴) → `reviewer-node` — see §D. 🟢 = qa-min only, 🟡/🔴 = qa-full + reviewer | If delivery carries NO `✅ GATES: ... qa✓` token → violation (hard gate, Bố duyệt 2026-07-29) |
| **Instinct repeat check** | `warren-style-embedding` §Instinct Ledger — check Session Log 3 dòng gần nhất | If pattern recurred → 🟡 block + báo "đã có instinct #X" |
| **Major decision (🟡 zone+)** — capital reallocation, conviction bet, bucket shift, policy change affecting ≥2 buckets | `review-plan` (adversarial) + **Munger Pre-Mortem Gate** (below) — inversion-first: "Điều gì sẽ kill cái này trong 30 ngày?" | If pre-mortem NOT done → 🔴 BLOCK. If top risk has no mitigation → flag + ask Bố |

## Insight / Idea / Actionable Checklist (the MISSING gate)
Before shipping any insight/idea/actionable, assert ALL:
- [ ] Data window ≥4 quý sạch (compressed/báo cáo thiếu = 0) — else STOP `[ANCHORS A7]`
- [ ] Every number cites source path + confidence tag `[HIGH]`/`[MOD]`/`[LOW]` — else tag `[UNKNOWN]`
- [ ] Actionable has owner + when + risk — not "buy now" alone
- [ ] No contradiction with `stock_vault/` SSOT (STOCK_MEMORY.md) — flag if conflict
- [ ] Not re-proposing a Bố-rejected ticker/thesis without new evidence
- [ ] Long-term thesis (A1) + risk assessment (A2) present

## Kill Criterion (the missing piece from Greg's tweet #5)
Tell Bố to shut it down when ANY:
1. **Data too thin** — <4 quý sạch → stop, ask Bố, do NOT proceed.
2. **Unsourced claim** — any conclusion without citeable source → stop, do NOT ship.
3. **Verify failed** — parser/LLM output not through `verify-parser-output` → UNTRUSTED.
4. **Rejected-reopen** — re-proposing a Bố-declined option without new evidence → stop.
5. **Ship-pressure signal** — if Hermes feels pressure to "just ship" over "ship correct" → pause, re-run gate.

## 🔴 Munger Pre-Mortem Gate — Inversion-First Decision Check

> **"Invert, always invert." — Charlie Munger.** Trước mọi major decision (🟡+), Hermes PHẢI chạy pre-mortem: giả định decision ĐÃ THẤT BẠI sau 30 ngày, rồi truy ngược "tại sao nó chết?"

### Trigger (BẮT BUỘC — không discretionary)
- Capital decision (mua/bán ≥5% portfolio, refill/shift bucket allocation)
- Conviction bet mới (all-in DCA vào 1 mã, mở vị thế BTC/Poly mới)
- Policy/procedure thay đổi ảnh hưởng ≥2 buckets (core/BTC/Poly)
- Initiative/case launch mới (thesis mới, sector mới)
- Warren nói "pre-mortem" / "Munger check" / "có chắc không"

### 6 Inversion Questions (trả lời TỪNG câu, print ra chat)
```
🔴 MUNGER PRE-MORTEM — [tên decision]:
Q1: Nếu 30 ngày sau cái này THẤT BẠI THẢM HẠI — nguyên nhân #1 là gì?
Q2: Ai / bộ phận nào có khả năng cao nhất làm nó fail? (con người, không phải "thị trường")
Q3: Assumption nào đang được tin nhất mà CHƯA có data xác nhận?
Q4: Nếu phải kill cái này trong 5 phút — lý do kill là gì?
Q5: Có ai trong team (research/broker/risk) sẽ ngầm phản đối / không cooperate?
Q6: Worst-case: thiệt hại tối đa nếu fail hoàn toàn? (tiền + thời gian + CX + morale)
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
| **Margin of Safety** | "Worst-case thiệt hại có chịu được không? Cần buffer bao nhiêu?" |
- **Circle of Competence** | "Mình (Warren/Hermes) có thực sự hiểu domain này? Hay đang đoán?" |
| **Incentives** | "Ai được lợi / ai bị thiệt từ decision này? Incentive của họ là gì?" |
- **Second-Order Effects** | "Hệ quả tiếp theo sau hệ quả đầu tiên là gì? (vd: all-in 1 mã → thiếu diversification → drawdown sâu)" |
| **Confirmation Bias** | "Mình đang tìm evidence ủng hộ hay đang thực sự test? Có bỏ qua data ngược không?" |

### Kill Criterion Integration
Nếu pre-mortem phát hiện BẤT KỲ điều nào sau đây → **🔴 NO-GO, flag Bố ngay:**
1. Top risk không có mitigation strategy
2. Worst-case thiệt hại > buffer chịu được
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

## D. Independent Dual-Agent Critic — FORCED for ALL profiles (2026-07-22, Bố duyệt)

> **🚨 UNIFIED OVERRIDE (2026-07-29, Bố duyệt — thêm qa-gate):** MỌI output loại **analysis / report / kết-luận-từ-data** PHẢI qua `qa-gate` → nếu PASS + zone 🟡/🔴 → spawn `reviewer-node`. 🟢 zone: qa-min only, no reviewer. **KHÔNG discretionary.** Áp dụng cho warren / stock / personal. verify-parser-output đã nằm trong qa-gate.

### Trigger (forced, no discretion — mọi profile)
- Warren: revenue summary, weekly ops synthesis, promo eval, dashboard, analysis từ vault data, insight từ số.
- Stock: research note / thesis draft / eval / buy-sell-hold call / dashboard / parser output.
- Personal: financial analysis, sleep/health insight từ data, legal doc analysis, bất kỳ conclusion-from-data.
- **Action:** run `qa-gate` (zone → qa-min/qa-full). If PASS + zone 🟡/🔴 → spawn `reviewer-node` (goal + context = output + domain checklist).
- **verify-parser-output** đã nằm trong qa-gate — không cần chạy riêng.
- **Kill-check:** nếu delivery KHÔNG có `🔍 REVIEWER:` token → violation (same class as missing boot / safenet token).
- Model: inherit free model từ chat (KHÔNG pin). Max 2 vòng + HARD BLOCK nếu FAIL lần 2 (escalate Bố).

### High-stakes (unchanged, cộng thêm)
Spawn critic độc lập qua `delegate_task` khi:
- Parser touching production / real vault data
- Plan with budget / financial impact
- Irreversible op (delete / rename / data removal)

Critic subagent gets ARTIFACT + CONTRACT (NOT Hermes's conclusion), adversarial prompt from `doubt-driven-development` Step 3. Reconcile findings against artifact — do NOT rubber-stamp (fresh reviewer can be wrong from lack of context).

## E. Prediction Ledger — Falsifiable Pre-Commitment Gate (borrowed từ hermes-self-evolution, 2026-07-26)

> **Principle:** Mọi major output / actionable có claim đo lường được → PHẢI log 1 prediction FALSIFIABLE (điều ta kỳ vọng xảy ra + metric để verify + due date) TRƯỚC khi deliver. Sau DUE, 1 pass (reviewer-node hoặc re-run) check thực tế → verdict confirmed/failed. Khớp với `verify-parser-output` (A6) + `cross-source-reconcile` (A7) đã có.

### Trigger (🟡+ hoặc mọi output có claim đo lường được)
- Warren analysis/report từ vault data có projection (vd "Rev/Cover LU5 tăng sau promo X")
- Stock buy/sell call có target price / timeframe
- Ops initiative có expected outcome đo lường được
- Parser/script thay đổi có expected behavior

### Format (ghi vào `vault/00_CORE_LOGIC/prediction_ledger.md`)
```markdown
## PREDICTION #N — YYYY-MM-DDTHH:MM+TZ
WITNESS: <friction/source thực — KHÔNG invent>
CHANGE: <hành động sắp làm>
EXPECTED: <kết quả kỳ vọng, đo lường được>
METRIC: <lệnh/command trả true/false — vd grep/wc/git/count>
DUE: <số cycle hoặc ngày>
```

### Rules
- 1 prediction / 1 actionable. NO-OP không log.
- Prediction PHẢI falsifiable — không viết được metric → drop (claim không đủ chặt để track).
- NEVER edit past entries. Verdict ghi vào `prediction_ledger.md` (section OUTCOME).
- Stale (>5 cycle không verdict) → auto-mark `failed` (unmeasured = loss).
- verify-parser-output PHẢI chạy TRƯỚC nếu prediction liên quan số.

### Kill-check integration
Nếu major output có claim đo lường được MÀ không log prediction → 🔴 BLOCK (thiếu pre-commitment, dễ bookkeeping theatre).

### Token (trên mọi gated output có prediction)
```
🔰 SAFENET: ✅ passed [prediction #N logged] — kill-check OK, routed to [gate]
```

---

## F. Failure-Signal Audit (OMH pattern — 2026-07-29)

> **Pattern absorbed from:** `rlaope/oh-my-hermes` `omh-failure-signal-audit` (MIT, 303★).  
> **Purpose:** Hunt silent failures before Bố discovers them from customer complaints. Cron chết âm thầm, parser trả sai số không báo lỗi, watcher ngừng watch.

### Finding Classifications

| Type | Triệu chứng | Ví dụ Warren |
|------|------------|-------------|
| **Swallowed Error** | `try/except: pass` hoặc exception bị bắt nhưng không log | Parser lỗi encoding → trả về 0 thay vì báo lỗi |
| **Dangerous Fallback** | Fallback value che dấu lỗi thật | Revenue = 0 → hiển thị "N/A" thay vì alert |
| **Propagation Gap** | Lỗi xảy ra ở tầng dưới, tầng trên không biết | Cron script lỗi → `sys.exit(0)` → Hermes báo OK |
| **False Green** | Status báo OK nhưng thực tế fail | `last_status=ok` nhưng script đã bị xóa 2 tháng trước |

### Detection Method (khi chạy `audit-automation`)

1. **Swallowed Error** → grep `except.*:\s*(pass|return None)` trong tất cả `.scripts/*.py`
2. **Dangerous Fallback** → grep `return 0\b|return ""|return \[\]|return {}\b` sau dòng gần `except`
3. **Propagation Gap** → check `sys.exit(0)` trong except block; check try/except không re-raise
4. **False Green** → cross-check `last_status=ok` vs file existence (`ls <script_path>`)

### Report Format

Mỗi finding:
```
🔴 [TYPE] <file>:<line> — <severity> — user impact: <gì>
   Fix: <smallest safe remediation — 1 dòng>
```

Severity: `CRITICAL` (Bố sẽ phát hiện từ khách hàng) / `HIGH` (mất data) / `MED` (có workaround) / `LOW` (cosmetic)

### Rule

- **No remediation claim** without observed fix evidence (run test, verify output, THEN claim fixed)
- **Never auto-fix** — each finding = propose Bố, đợi approve, mới sửa
- Audit frequency: mỗi lần chạy `audit-automation` hoặc khi Bố nói "check cron có con nào chết không"

---

## Pitfalls
- **Doubt theater**: self-review of own output = shared blind spot. Use D (independent) for high-stakes; routing gate suffices for low-stakes.
- **Token without gate**: never emit ✅ without actually running the routed check.
- **Over-gating**: low-stakes (lookup, summarize) → skip heavy gate, but still emit `🔰 SAFENET: ✅ passed [lookup]` (cheap, proves discipline).
- **Silent skip**: if gate would block, say 🔴 + reason. Never hide.
- **Lean**: xem nguyên tắc router ở intro — không duplicate logic của skill được route.
