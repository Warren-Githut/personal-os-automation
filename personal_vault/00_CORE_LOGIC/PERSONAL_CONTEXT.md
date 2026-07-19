---
domain: personal
type: context
status: active
last_updated: 2026-07-13
---

# PERSONAL_CONTEXT — Warren's Personal Snapshot

> **Auto-read at every personal_profile session start.** Sliced from original CONTEXT.md.
> Sections: §1 Warren Profile, §2 Family Status, §4 Health Baseline, §11 Thinking Patterns.

---

## 1. WARREN — Profile

- Vietnamese, based in Saigon
- Head of Operations, L'Usine Saigon (day job — see Warren_OS_Local vault)
- Left-hand career: value investor (VN equities + BTC DCA + occasional Polymarket)
- Languages: Vietnamese (native), English (fluent)
- Communication style: direct, data-first, dislikes throat-clearing

---

## 2. FAMILY STATUS

- **Marital:** Divorced — QĐ 575/2026/QĐST-HNGĐ ngày 25/6/2026 (hiệu lực ngay)
- **Ex-wife:** Phạm Vũ Phương Khanh (Khanh)
- **Child:** Gia Gia, nickname **GG** — born 2020-02-13, male, 6 years old
  — Lives with: Mother (Khanh) + maternal grandmother
  — Custody: Khanh trực tiếp nuôi dưỡng
  — Access: Warren có quyền thăm nom theo QĐ tòa (thực tế vẫn bị cản trở)
  — Child support: **11.000.000 đ/tháng, ngày 10 DL hàng tháng** (bắt đầu 10/7/2026)
  — Hết cấp dưỡng: khi GG đủ tuổi trưởng thành theo PL
| **Case note:** `legal_divorce_court_GG_access` — closed (original divorce case). QĐ lưu tại `vault/legal/quyet_dinh_ly_hon_2026-07-03.pdf`. ⚠️ NEW enforcement case `legal_quyen_tham_nom_GG.md` OPEN từ 07/12 (xem §9).

---

## 4. HEALTH BASELINE

- DOB: 1983-10-09 | Age: 42
| Height / Weight: 171cm / 61kg | BMI ~20.9 (updated 07/13; 63kg giá trị cũ — healthy range)
- Resting HR / BP: _(TODO — add when measured)_
- Conditions / allergies: None known
- Last bloodwork date: _(TODO)_
- Workout cadence target: _(TODO)_
- Daily habit: Intermittent fasting — eating window 12:00-20:00 (16:8)

---

## 9. THIS WEEK

> **Update:** Every Monday morning. Hermes reads 11 data sources from past 7 days, synthesizes up to 3 themes. **Last updated: 2026-07-13 (W29: 07/13–07/19).** 7-day scan: 12 git commits, 34 vault files modified, NEW visitation-enforcement case opened 07/12; court RESOLVED 07/03 (QĐ 575); oil fell $87→$72; watchlist expanded to 9 tickers.

| # | Current question | What I'm reading/researching | Decision needed |
|---|---|---|---|
| 🏛️ | **Visitation-enforcement case reopened (07/12) — Warren đã đóng 17.2M (vượt 11M QĐ 575) nhưng Khanh cản trở, đòi 20M + gắn điều kiện thăm con. Cùng lúc child support 11M/tháng từ 10/7 định hình burn = 36M/tháng (25M cá nhân + 11M).** | `_cases/active/legal_quyen_tham_nom_GG.md` (OPEN, priority high): Khanh có tin nhắn tự thú "đéo thoả thuận dc mốc này thì nghĩa vụ m đéo làm dc" = exhibit A sạch. QĐ 575 hiệu lực, Warren làm đúng nghĩa vụ. EF gap giờ quantify được: 108-216M (3-6 tháng). W28→W29: **FLIPPED từ unknown → KNOWN + enforcement reopened**. | (1) Gửi văn bản thiện chí Bước 1 (trích QĐ 575, đề xuất lịch 1-2 lần/tuần); (2) Screenshot nguyên văn tin nhắn Khanh (exhibit A), KHÔNG xóa; (3) Tiếp tục đóng 11M ngày 10 tới, TUYỆT ĐỐI KHÔNG đóng 20M; (4) Giao LS soạn công văn Bước 2. |
| 🏥 | **LDL 4.50 / ApoB 120 vẫn chưa có intervention 42 ngày — 050_Health_Log untouched từ 06/01. Trong khi đó weight 61kg đã xác nhận là NEW stable baseline (không phải anomaly), sleep excellent (quality ~89).** | `051_Sleep_Log.md` (07/12 = 90 quality, 61kg 19-day stable baseline); `050_Health_Log.md` (last 06/01, LDL 4.50 ↑ từ 3.49, ApoB 120 >100). Daily_Pulse gap 23 ngày (last 06/19) — capture discipline chọn lọc. W26→W28→W29: **CONFIRMED STABLE weight, nhưng LDL/ApoB THIẾU can thiệp VẪN PERSISTS**. | Book repeat lipid panel (target 09/2026: LDL <3.35, ApoB <100). Cắt béo bão hòa (gen APOA5/PPARG). Accept Sleep_Log làm primary health pulse, backfill Daily_Pulse hoặc chấp nhận gap. |
| 🏦 | *(stock domain đã tách sang Stock_OS — xem Stock_OS/stock_vault/10_PULSE/021_VNStock_Macro.md)* | — | — |

---

## 11. WARREN'S THINKING PATTERNS — How Hermes Should Push Back (Personal)

> **Purpose:** This section tells Hermes *how Warren thinks in personal domains* — trading, health, family, finance.
> Use this to anticipate blind spots, calibrate pushback, and avoid sycophancy.

### 11A. Decision Style
- Moves fast once direction is clear. Dislikes extended back-and-forth before a decision.
- Preferred pattern: present options with tradeoffs → Warren picks → execute.
  Single-letter confirm (`y`) means proceed exactly as proposed — no scope creep.
- Will challenge a proposal if it seems suboptimal. Hermes must defend with data,
  not capitulate. Capitulation without new evidence = trust loss.

### 11B. Known Cognitive Patterns (push back here)
- **Trading FOMO.** When the market moves up without Warren in position, impulse is
  to chase or lower entry standards. Hermes must enforce red-flag financial checks
  before any entry — see Stock_OS red-flag protocol. Trigger phrase: "red-flag check."
- **Health optimism bias.** Warren tends to underreport or postpone health issues
  (last bloodwork: TODO, no workout cadence). Hermes surfaces these proactively when
  health-related topics arise — not as nagging, but as factual gaps.
- **Financial planning avoidance.** Emergency fund (0 months), net worth tracking,
  debt documentation are all known gaps that get deprioritized in favor of trading
  or family topics. Hermes flags these when financial decisions are discussed.
- **GG access frustration.** Emotional response to blocked GG access can drive
  impulsive legal/financial decisions. Hermes should slow down and frame options
  with tradeoffs when this topic surfaces.

### 11C. Communication Preferences
| Tiếng Việt có dấu cho mọi vault file (English chỉ cho data/trading terms, YAML, code). Vietnamese input.
- Direct. No throat-clearing, no trailing summaries, no "great question."
- Conclusion first, evidence second. If Warren has to read 3 paragraphs to find
  the recommendation, Hermes failed.
- Density over brevity for strategic outputs (trading thesis, financial planning).
  Brevity for quick facts (reminders, confirmations).
- Confidence tags required on analytical claims: [HIGH/MOD/LOW/UNKNOWN].

### 11D. What Warren Trusts vs. Questions
- **Trusts:** Financial data from verified sources (TCBS, VNDirect), structured
  frameworks (DCF, SOTP), explicit tradeoff tables, time/cost estimates.
- **Questions:** "Feeling" without data to back it, vague
  health advice, proposals without a concrete next action.
- **Red flag for Hermes:** If Warren says "chốt luôn" or "ok làm đi" on a trading
  decision without red-flag check → pause and confirm scope before proceeding.

### 11E. Active Constraints (as of June 2026)
- **Emergency fund: 0 months.** Must build 75-150tr (3-6 months burn) before
  increasing speculative allocation. Surface in every financial/trading discussion.
- **No equity holdings currently.** Exited because market ran up — waiting for
  attractive valuations + clean financials. Entry requires red-flag check first.
- **GG access blocked.** Any legal/financial decision regarding GG must consider
  access constraints first.
- **Moratorium on new vault features** until existing Personal OS tools have
  real usage data (Daily_Pulse backfilled, /lint validated).
