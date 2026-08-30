---
domain: personal
type: context
status: active
last_updated: 2026-08-17
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
- Last bloodwork date: 2026-06-11 — LDL 4.50 / ApoB 120 (⚠️ **67 ngày** chưa có can thiệp nào ghi nhận; `050_Health_Log.md` chưa chạm **77 ngày**, từ 01/06)
- Workout cadence target: _(TODO — thực tế logged = 0)_
- Daily habit: Intermittent fasting — **20h/ngày, 6/6 ngày capture tuần W33 (10–15/08)**, khoá liên tục từ W32 (leo thang từ 18h; eating window thu hẹp so với 16:8 gốc)

---

## 9. THIS WEEK

> **Update:** Every Monday morning. Hermes reads 11 data sources from past 7 days, synthesizes up to 3 themes. **Last updated: 2026-08-17 (W34: 08/17–08/23).** 7-day scan (cửa sổ 10/08–16/08 = W33): 18 git commits, 15 vault file thay đổi, `_inbox/01_unprocessed/` = 0 item (abolished 2026-08-30), sleep capture 6/7 ngày (thiếu 08-16), `_growth/COMMUNICATION_SKILL_WITH_GG.md` mới (16/08), W33 weekly_connections phải viết bù hôm nay 09:09 (cron Chủ Nhật 16/08 skip). Verify gate: PASS (recompute độc lập, 0 dòng drop).

| # | Current question | What I'm reading/researching | Decision needed |
|---|---|---|---|
| 🏛️ | **Đã chuyển 11M cấp dưỡng tháng 8 chưa — hạn 10/08 đã qua 7 ngày và vault KHÔNG có một bằng chứng nào. Case thăm nom STALE 36 ngày, 8/8 checklist vẫn `[ ]`, không nhúc nhích từ 12/07.** | `_cases/active/legal_quyen_tham_nom_GG.md` (status OPEN, opened 12/07, `last_updated: 2026-07-12` = **36 ngày**; grep: 8 `[ ]` / 0 `[x]`; không có field `follow_up` → không auto-reset — file VẪN TỒN TẠI, 17KB, claim "BIẾN MẤT" ở §9 cũ là SAI và đã bị xoá khỏi đây); `10_PULSE/weekly_connections_log.md` W33 #1 (feed [HIGH]: thanh toán T8 chưa xác nhận); `30_KNOWLEDGE_BASE/wiki/log.md` (escalation chạy đều 30d→31d→33d→34d→35d, 6 chu kỳ không sinh ra hành động nào); `00_CORE_LOGIC/PERSONAL_CONTEXT.md` §2 (QĐ 575 — 11M ngày 10 DL). Điểm sáng duy nhất mặt trận GG tuần này: `_growth/COMMUNICATION_SKILL_WITH_GG.md` (16/08) — 4 câu hỏi mở thay "hôm nay đi học thế nào", capture parenting đầu tiên sau nhiều tuần, dùng được ngay khi có lịch gặp. W30→W34: **PERSISTS + XẤU ĐI** (stale 7d → 36d qua 4 kỳ). | (1) Xác nhận đã chuyển 11M T8: nếu rồi → tick #8 + lưu biên lai (B2) NGAY để vault có chứng cứ trước Tòa; nếu chưa → chuyển đúng **11M**, TUYỆT ĐỐI KHÔNG 20M theo yêu sách của Khanh. (2) Chốt B6: screenshot exhibit A (tin nhắn Khanh tự thú), KHÔNG xoá hội thoại. (3) Hạn kế tiếp **10/09 — còn 24 ngày**: đặt nhắc để không lặp vòng "quá hạn 7 ngày, vault mù". |
| 🏥 | **Nhịn ăn 20h khoá 6/6 ngày mà cân 62kg đóng băng 33 entry liên tiếp — trong khi LDL 4.50 / ApoB 120 đã 67 ngày chưa đo lại. Đòn bẩy duy nhất đang không nhắm vào mục tiêu.** | `10_PULSE/051_Sleep_Log.md` W33 (6 entry 10–15/08): ngủ TB **7h37** (45.667h ÷ 6 = 7.6111h), quality TB **86.0** (516 ÷ 6), fasting **20h × 6**, **62kg × 6**, BP 97/71–72 — verify gate PASS, 0 dòng drop. So W32 (7/7 ngày): ngủ 7h27 → 7h37 (**+0.16h**) nhưng quality 88.57 → 86.0 (**−2.57**) → ngủ dài hơn mà chất lượng đi lùi. Streak 62kg thực tế bắt đầu **14/07** (33 entry, không phải 27/07 như ghi chú cũ) = 34 ngày cân không nhúc nhích. `10_PULSE/050_Health_Log.md` `last_updated: 2026-06-01` → **77 ngày** không chạm; panel 11/06 chưa có bất kỳ can thiệp dinh dưỡng nào logged; workout logged = 0. Thiếu data 08-16 (bot chưa commit sáng nay, chưa quá ngưỡng 3 ngày → chưa đỏ). W30→W34: **NGHỊCH LÝ KÉO DÀI** (LDL gap 49d → 67d). | (1) Đặt lịch **lipid panel lại trong tháng 8** — mục tiêu 09/2026: LDL <3.35, ApoB <100 (còn ~1 tháng để có số trước mốc). (2) Cắt béo bão hoà (gen APOA5/PPARG) thay vì nâng thêm giờ nhịn — 20h × 34 ngày đã chứng minh vô hiệu với cân nặng. (3) Quyết dứt `050_Health_Log`: mở lại hay khai tử — 77 ngày trống làm health baseline mù ngoài mảng ngủ. |
| 🧹 | **Vault chỉ còn ĐÚNG MỘT mạch dữ liệu chạy đúng (Telegram sleep capture). Daily_Pulse chết 59 ngày, triplicate 07-30 treo 18 ngày, cron weekly Chủ Nhật skip. Tiền: 0 EF + 11M/tháng → vốn vẫn khoá, trading đã ra khỏi vault này.** | `10_PULSE/Daily_Pulse.md` (entry cuối 19/06 → gap **59 ngày**; 4 domain GG/Money/Mind/People tịt ngóm từ giữa tháng 6); `10_PULSE/051_Sleep_Log.md` (`### 2026-07-30` lặp **×3**, dup scan xác nhận chỉ ngày này lặp — **18 ngày** chưa dọn; `capture-sleep` read-only nên không tự sửa); `10_PULSE/weekly_connections_log.md` (W33 viết bù 09:09 hôm nay vì cron CN 16/08 không chạy — lần miss thứ 2 trong 5 tuần, trước đó W30+W31 mất trắng); `10_PULSE/051_Sleep_Log.csv` (mồ côi **39 ngày**, dừng 09/07); `_inbox/01_unprocessed/` = 0 item (abolished). Trading: stock domain đã purge sang Stock_OS (13/07, `528b2c6`) → personal vault không còn watchlist/thesis; ràng buộc **0 EF + 11M/tháng drain** nguyên vẹn; FTSE EM upgrade 21/09 còn **35 ngày** (theo vault, [MOD]). W30→W34: **META GAP MỞ RỘNG** (gap 29d → 59d). | (1) Xoá 2 bản `### 2026-07-30` trùng trong Sleep_Log, giữ 1 — việc 2 phút, đã treo 18 ngày và đang làm nhiễu mọi lần scan. (2) Quyết dứt điểm Daily_Pulse: khai tử hay nối lại (gap 59 ngày tự nó đã trả lời) + `051_Sleep_Log.csv` mồ côi. (3) Check scheduler máy Chủ Nhật — cron weekly miss 2/5 tuần. (4) Mọi bàn luận xuống tiền → mở Stock_OS, và vẫn phải qua cửa 0 EF + 11M drain trước khi nói tới entry. |

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
