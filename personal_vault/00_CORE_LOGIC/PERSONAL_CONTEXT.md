---
domain: personal
type: context
status: active
last_updated: 2026-07-20
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

> **Update:** Every Monday morning. Hermes reads 11 data sources from past 7 days, synthesizes up to 3 themes. **Last updated: 2026-07-20 (W30: 07/20–07/26).** 7-day scan: 12 git commits (07/13–07/20), vault files modified (health capture + weekly_connections), stock domain purged to Stock_OS (07/13, `528b2c6`), `_cases/active/` EMPTY, Daily_Pulse gap 29+ ngày.

| # | Current question | What I'm reading/researching | Decision needed |
|---|---|---|---|
| 🏛️ | **⚠️ Visitation-enforcement case FILE ĐÃ BIẾN MẤT khỏi vault — W29 (07/13) ghi `legal_quyen_tham_nom_GG.md` OPEN/STALE, nhưng scan 07/20: `_cases/active/` RỖNG, file không tồn tại ở bất kỳ đâu trong `_cases/`. Court divorce case vẫn CLOSED zero-churn (7 ngày confirm).** | `weekly_connections_log.md` W29 (#2) — flag case STALE 7d, Action Checklist all `[ ]`; nhưng `search_files` toàn vault = 0 kết quả cho "tham_nom/visitation/access" trong `_cases/`. Khả năng: (a) case đã được resolve + move sang `_cases/closed/` nhưng chưa log, hoặc (b) file bị purge cùng đợt Stock_OS split (07/13) mà không archive. Child support 11M/tháng + 17.2M đã đóng vẫn nguyên. W29→W30: **CASE FILE MẤT TÍCH — CẦN XÁC NHẬN**. | (1) Xác nhận với Warren: case thăm nom đã xong (move sang closed) hay bị mất file? (2) Nếu còn active → recreate file từ exhibit A (tin nhắn Khanh) + Action Checklist; (3) Tiếp tục đóng 11M ngày 10 tới, KHÔNG đóng 20M. |
| 🏥 | **LDL 4.50 / ApoB 120 vẫn chưa có intervention 49 ngày — 050_Health_Log untouched từ 06/01. Weight 61→62kg (+1kg, W28→W29), BMI ~21.2 healthy. Sleep excellent (quality 88-92).** | `051_Sleep_Log.md` (07/13=61kg → 07/14-19=62kg consistent, 7 entries; BP 96-99/71-72 normal; fasting 18h stable); `050_Health_Log.md` (last_updated 06/01, LDL/ApoB gap 49d). Daily_Pulse gap 29+ ngày (last 06/19) — capture regression tiếp diễn. W29→W30: **WEIGHT +1kg STABLE, LDL/ApoB GAP WIDENS 42→49d, Daily_Pulse GAP 23→29d**. | Book repeat lipid panel (target 09/2026: LDL <3.35, ApoB <100). Cắt béo bão hòa (gen APOA5/PPARG). Accept Sleep_Log làm primary; backfill Daily_Pulse hoặc chấp nhận gap (đã 29 ngày). |
| 🏦 | **Stock domain đã tách hoàn toàn sang Stock_OS (07/13, git `528b2c6`) — personal vault KHÔNG còn trading pulse. 0 EF + 11M/tháng drain nguyên, capital vẫn blocked.** | `weekly_connections_log.md` W29 (#1): Candidates_Watchlist + theses (PVD/GAS/MWG/NLG/PNJ/HPC/FPT/VCB/BID) purged khỏi personal_vault. Weekly synthesis phải cross-reference Stock_OS thay vì vault này. Catalyst tracking (FTSE Sep 21, LDR easing) giờ tách rời khỏi personal context. W29→W30: **STRUCTURAL SPLIT — trading ra khỏi scope cá nhân**. | Không action trong personal vault. Khi bàn trading → mở Stock_OS. Vẫn flag 0 EF + 11M drain mỗi khi Warren định xuống tiền. |

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
