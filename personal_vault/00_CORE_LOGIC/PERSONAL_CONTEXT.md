---
domain: personal
type: context
status: active
last_updated: 2026-09-07
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
- Height / Weight: 171cm / **62kg** | BMI ~21.2 (verified 17/08/2026 — 62kg khoá **33 entry liên tiếp, 14/07–15/08** trong `10_PULSE/051_Sleep_Log.md`; mốc "27/07" ghi ngày 10/08 là sai, streak bắt đầu từ 14/07)
- Resting HR / BP: BP 97/71–72 (dải quan sát 6 ngày W33, bình thường) | Resting HR _(TODO)_
- Conditions / allergies: None known
- Last bloodwork date: 2026-08-05 — LDL 3.94 / ApoB 99 (✅ đã cập nhận từ PDF 26020536566; `050_Bloodwork_Update.md` đã log)
- Workout cadence target: _(TODO — thực tế logged = 0)_
- Daily habit: Intermittent fasting — **20h/ngày, 6/6 ngày capture tuần W33 (10–15/08)**, khoá liên tục từ W32 (leo thang từ 18h; eating window thu hẹp so với 16:8 gốc)

---

## 9. THIS WEEK

> **Update:** Every Monday morning. Hermes reads 11 data sources from past 7 days, synthesizes up to 3 themes. **Last updated: 2026-09-07 (W36: 09/07–09/13).** 7-day scan (cửa sổ 08/31–06/09 = W35): 15 git commits, 12 vault file thay đổi, sleep capture GREEN (09-05 entry cuối, gap 2 ngày < ngưỡng 3), `_inbox/01_unprocessed/` = abolished (2026-08-30), `050_Bloodwork_Update.md` nhận entry 08/05 (LDL 3.94, ApoB 99.22), `personal-health-checkup` v2.2.0 synced. Weekly connections W35 CHƯA viết (cron Chủ Nhật 06/09 skip).

| # | Current question | What I'm reading/researching | Decision needed |
|---|---|---|---|
| 🏛️ | **Cấp dưỡng 11M tháng 9 — hạn 10/09 chỉ còn 3 ngày, vault vẫn KHÔNG có bằng chứng T8 (đã quá hạn 28 ngày). Case thăm nom STALE 56 ngày, 8/8 `[ ]`.** | `_cases/active/legal_quyen_tham_nom_GG.md` (status OPEN, opened 12/07, `last_updated: 2026-07-12` = **56 ngày**; grep: 8 `[ ]` / 0 `[x]`; không có field `follow_up` → không auto-reset); `30_KNOWLEDGE_BASE/wiki/log.md` (escalation chạy đều 51d→52d→54d→55d→56d, 5 chu kỳ không sinh ra hành động); `00_CORE_LOGIC/PERSONAL_CONTEXT.md` §2 (QĐ 575 — 11M ngày 10 DL). W34→W36: **PERSISTS + XẤU ĐI** (stale 36d → 56d qua 2 kỳ). | (1) **Hạn 10/09 chỉ còn 3 ngày** — xác nhận đã chuyển 11M T9 (và T8 nếu còn thiếu): nếu rồi → tick #8 + lưu biên lai (B2) NGAY; nếu chưa → chuyển đúng **11M**, TUYỆT ĐỐI KHÔNG 20M. (2) Chốt B6: screenshot exhibit A (tin nhắn Khanh tự thú), KHÔNG xoá hội thoại. (3) Sau khi chuyển → cập nhật vault ngay để có chứng cứ trước Tòa. |
| 🏥 | **LDL 3.94 / ApoB 99.22 (08/05) — cải thiện nhưng vượt mục tiêu. Cholesterol TP 5.99 ngưỡng cao. Mục tiêu 09/2026 sắp tới.** | `10_PULSE/050_Bloodwork_Update.md` (entry mới nhất 08/05: LDL 3.94 giảm từ 4.50, ApoB 99.22 giảm từ 120, Chol TP 5.99 ngưỡng cao, HbA1c 5.5% ổn, CRP không có trong panel này); `10_PULSE/051_Sleep_Log.md` W35 (08/31–09/05, 7 ngày capture): ngủ TB ~7h34, quality TB ~88.6, fasting **20h × 7**, **62kg × 7**, BP 97/71–72. Streak 62kg khoá **54+ ngày** (từ 14/07). W34→W36: **CẢI THIỆN** (LDL 4.50→3.94, ApoB 120→99.22). | (1) Mục tiêu 09/2026 (LDL <3.35, ApoB <100) — LDL vẫn còn cao hơn mục tiêu, ApoB gần mục tiêu. Tiếp tục cắt béo bão hoà. (2) **Lặp lipid panel lại** trong tháng 9 để đánh giá xem xu hướng giảm có bền vững không. (3) Nhịn 20h khoá 54+ ngày mà cân không nhúc nhích → cần thay đổi chiến lược nếu mục tiêu là giảm cân. |
| 🧹 | **Vault chỉ còn ĐÚNG MỘT mạch dữ liệu chạy đúng (Telegram sleep capture). Daily_Pulse chết 79 ngày, triplicate 07-30 treo 38 ngày. Chỉ 1 mạch hoạt động.** | `10_PULSE/Daily_Pulse.md` (entry cuối 19/06 → gap **79 ngày**; 4 domain GG/Money/Mind/People tịt ngóm từ giữa tháng 6); `10_PULSE/051_Sleep_Log.md` (`### 2026-07-30` lặp **×3**, dup scan xác nhận chỉ ngày này lặp — **38 ngày** chưa dọn; `capture-sleep` read-only nên không tự sửa); `10_PULSE/weekly_connections_log.md` (W35 CHƯA viết — cron Chủ Nhật 06/09 skip); `10_PULSE/051_Sleep_Log.csv` (mồ côi **59 ngày**, dừng 09/07); `_inbox/01_unprocessed/` = abolished (2026-08-30). Trading: stock domain đã purge sang Stock_OS (13/07, `528b2c6`) → personal vault không còn watchlist/thesis; ràng buộc **0 EF + 11M/tháng drain** nguyên vẹn. W34→W36: **META GAP MỞ RỘNG** (gap 59d → 79d, triplicate 18d → 38d). | (1) Xoá 2 bản `### 2026-07-30` trùng trong Sleep_Log, giữ 1 — việc 2 phút, đã treo 38 ngày và đang làm nhiễu mọi lần scan. (2) Quyết dứt điểm Daily_Pulse: khai tử hay nối lại (gap 79 ngày tự nó đã trả lời) + `051_Sleep_Log.csv` mồ côi. (3) Check scheduler máy Chủ Nhật — cron weekly skip Chủ Nhật. (4) Mọi bàn luận xuống tiền → mở Stock_OS, và vẫn phải qua cửa 0 EF + 11M drain trước khi nói tới entry. |

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
