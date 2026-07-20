---
last_updated: 2026-07-20
domain: meta
type: pulse
status: active
tags:
  - weekly-connections
  - cross-domain
entries: 8
related:
  - ../00_CORE_LOGIC/STOCK_CONTEXT.md
  - ../00_CORE_LOGIC/PERSONAL_CONTEXT.md
  - ../00_CORE_LOGIC/HOME.md
---

# Weekly Connections Log

## 2026-W29 (13/07–19/07)

| # | Connection | Domains | Evidence | Signal |
|---|---|---|---|---|
| 1 | **Stock domain PURGED from Personal_OS (07/13) — trading data moved to Stock_OS, breaking the trading↔finance cross-domain chain that W22-W28 tracked** — Git commit `528b2c6` ("split stock domain to Stock_OS: purge stock files and rewrite indices") removed Candidates_Watchlist, 020_VNStock_Weekly_Outlook, 021_VNStock_Macro, company theses (PVD/GAS/MWG/NLG/PNJ/HPC/FPT/VCB/BID) khỏi personal_vault. PERSONAL_CONTEXT §9 xác nhận: "stock domain đã tách sang Stock_OS". Hệ quả: weekly_connections không còn đọc được trading pulse trực tiếp từ personal vault → connection #3/#4 từ W24-W28 (oil vs PVD/GAS, watchlist widening) giờ phải cross-reference Stock_OS. 0 EF + 11M/month drain vẫn nguyên, nhưng catalyst tracking tách rời. | trading ↔ meta ↔ finance | [git log](../.git/log) (`528b2c6` 07/13 stock split); [PERSONAL_CONTEXT §9](../00_CORE_LOGIC/PERSONAL_CONTEXT.md) ("stock domain đã tách sang Stock_OS"); [weekly_connections_log W28](../10_PULSE/weekly_connections_log.md) (#3/#4 traded on 021_Macro + Watchlist — nay purged) | 🟡 Contradiction — W28→W29: **STRUCTURAL SPLIT** |
| 2 | **Visitation-enforcement case STALE 7 days — Warren paid 17.2M, Khanh obstructs, but ZERO of 8 Action Checklist items executed (no Bước 1 văn bản, no exhibit A screenshot, no lawyer letter)** — Case `legal_quyen_tham_nom_GG.md` OPEN từ 07/12, last_updated 07/12. Qua 7 ngày không có update mới. Action Checklist (#1-#8) toàn bộ `[ ]` — chưa gửi văn bản thiện chí Bước 1, chưa screenshot tin nhắn Khanh (exhibit A), chưa giao LS soạn công văn Bước 2. Warren đã làm đúng nghĩa vụ tài chính (17.2M > 11M) nhưng mặt trận pháp lý hoàn toàn tĩnh. Khanh có tin nhắn tự thú "đéo thoả thuận dc mốc này thì nghĩa vụ m đéo làm dc" = exhibit A sạch đang bị bỏ phí. | legal ↔ family_gg | [`legal_quyen_tham_nom_GG.md`](../_cases/active/legal_quyen_tham_nom_GG.md) (OPEN 07/12, Action Checklist all `[ ]`, last_updated 07/12); [PERSONAL_CONTEXT §9](../00_CORE_LOGIC/PERSONAL_CONTEXT.md) (case reopened, Warren paid 17.2M); [log.md](../30_KNOWLEDGE_BASE/wiki/log.md) (07/13-07/19: no visitation update, only court CLOSED flags) | 🔴 Critical gap — W28→W29: **STALE (no action 7d)** |
| 3 | **Weight ticked UP 61→62kg while LDL/ApoB intervention STILL missing 49 days — health data disciplined via Sleep_Log, but 050_Health_Log untouched since 06/01** — W28 xác nhận 61kg = new stable baseline (19d). W29: 07/13=61kg → 07/14 onward = 62kg consistent (6 entries). +1kg trong 1 tuần, vẫn trong healthy range (BMI ~21.2). NHƯNG: 050_Health_Log last_updated 06/01 → LDL 4.50/ApoB 120 từ panel 06/11 VẪN chưa có dietary intervention logged (49 ngày). Sleep quality avg ~88 (07/16 dip to 80), BP 96-99/71-72 normal, fasting 18h consistent. Meta: capture discipline vẫn chọn lọc — Sleep_Log excellent, Daily_Pulse 29-day gap, 050_Health_Log 49-day gap. | health ↔ meta | [051_Sleep_Log](../10_PULSE/051_Sleep_Log.md) (07/13=61kg → 07/14-19=62kg, 7 entries); [050_Health_Log](../10_PULSE/050_Health_Log.md) (last_updated 06/01, LDL/ApoB unaddressed); [Daily_Pulse](../10_PULSE/Daily_Pulse.md) (last 06/19, 29-day gap); [log.md](../30_KNOWLEDGE_BASE/wiki/log.md) (07/13-19: Daily_Pulse gap 26→29 ngày) | 🟡 Correlation — W28→W29: **WEIGHT +1kg, LDL GAP WIDENS** |
| 4 | **Daily_Pulse gap now 29 days (was 23 in W28) — capture discipline regression in the 5-bullet journal while Sleep_Log stays pristine** — W28 flagged Daily_Pulse gap 23 ngày. W29: gap lên 29 ngày (last entry 06/19). Process-notes cron chạy sạch mỗi ngày nhưng không có input mới từ Warren. Sleep_Log (051) vẫn được update thủ công đều đặn (07/19 = entry mới nhất). Nghịch lý: health pulse riêng hoạt động tốt, nhưng tổng hợp 5-domain (GG/Money/Mind/People) hoàn toàn tịt ngóm. Không có GG contact log, không có Money note, không có People note trong 29 ngày. | meta ↔ family_gg ↔ finance | [Daily_Pulse](../10_PULSE/Daily_Pulse.md) (last 06/19); [051_Sleep_Log](../10_PULSE/051_Sleep_Log.md) (07/19 active); [log.md](../30_KNOWLEDGE_BASE/wiki/log.md) (07/13-19 daily "Daily_Pulse.md gap 26→29 ngày") | 🟡 Correlation — W28→W29: **GAP WIDENED 23→29d** |
| 5 | **Court CLOSED status rock-stable across W29 — 7 consecutive daily confirmations, no follow_up churn, blocker #1 from W22-W27 officially dead** — Log.md ghi "RESOLVED: Court case CLOSED" mỗi ngày 07/13→07/19 (7 lần). QĐ 575/2026/QĐST-HNGĐ thuận tình ly hôn, GG ở với mẹ, Warren cấp dưỡng 11M/tháng. File tại `_cases/closed/`. Không còn follow_up check (status không đổi từ 07/03). So với W22-W27 (16-day critical gap, follow_up reset 5 lần) → giờ là zero-churn stable state. Đây là nền tảng vững cho các quyết định tài chính/thăm nom. | legal ↔ family_gg | [log.md](../30_KNOWLEDGE_BASE/wiki/log.md) (07/13-19: 7× "Court case CLOSED" flags); [`_cases/closed/legal_divorce_court_GG_access.md`](../_cases/closed/legal_divorce_court_GG_access.md) (status CLOSED); [PERSONAL_CONTEXT §2](../00_CORE_LOGIC/PERSONAL_CONTEXT.md) (divorced, 11M/month) | 🟢 Amplification — W28→W29: **STABLE (zero churn)** |

**📊 Stats:** 5 connections | 6 domains involved (trading, meta, finance, legal, family_gg, health)

**🔗 Most connected domain:** meta (appears in 3 of 5 connections: #1, #3, #4)

**🔄 Previous week (W28) comparison:**
| Connection | W28 status | W29 change |
|---|---|---|
| #1 (court RESOLVED, visitation reopened) | 🔴 Critical gap → RESOLVED + NEW | **SPLIT** — trading data purged to Stock_OS (07/13), visitation case now STALE 7d |
| #2 (visitation-enforcement OPEN) | 🔴 Critical gap — NEW | **STALE** — no action in 7 days, checklist all `[ ]` |
| #3 (weight 61kg stable, LDL missing 42d) | 🟡 Correlation — CONFIRMED STABLE | **WEIGHT +1kg (61→62), LDL gap 42→49d** |
| #4 (capture discipline selective) | 🟡 Correlation — SELECTIVE PERSISTS | **REGRESSED** — Daily_Pulse gap 23→29d |
| #5 (court CLOSED stable) | 🟢 Amplification — RESOLVED | **ZERO CHURN** — 7 consecutive daily confirmations |

**💡 Feed into /personal-context-update (Monday):**
1. **[HIGH] Visitation case STALE 7 days — Action Checklist all `[ ]`.** Gửi văn bản Bước 1 (trích QĐ 575, đề xuất lịch 1-2 lần/tuần) + screenshot tin nhắn Khanh (exhibit A) NGAY. 17.2M đã đóng, vị thế mạnh, nhưng tĩnh = bỏ phí leverage.
2. **[MOD] Stock domain split → trading tracking moved to Stock_OS.** Weekly cross-domain synthesis phải cross-reference Stock_OS thay vì personal vault. 0 EF + 11M drain vẫn nguyên, catalyst view tách rời.
3. **[MOD] Health: weight 62kg (+1kg), LDL/ApoB intervention STILL missing 49 days.** 050_Health_Log untouched since 06/01. Book repeat lipid panel (target 09/2026). Sleep_Log excellent (7d, quality ~88).
4. **[MOD] Daily_Pulse gap 29 days — capture regression.** Sleep_Log active but 5-bullet journal dead. Backfill or accept Sleep_Log as primary; log GG contact + Money notes manually.
5. **[LOW] Court CLOSED stable 7 days — zero churn.** No action needed; baseline confirmed.

---

## 2026-W28 (06/07–12/07)

| # | Connection | Domains | Evidence | Signal |
|---|---|---|---|---|
| 1 | **Court case RESOLVED (07/03) — QĐ 575 defines 11M/month child support + visitation rights, ending the 16-day critical gap that paralyzed 4 domains** — Phiên tòa kết thúc 07/03 với QĐ 575/2026/QĐST-HNGĐ (25/6/2026, hiệu lực ngay). Case file chuyển `_cases/closed/`. Child support được xác định rõ: **11.000.000 đ/tháng, ngày 10 DL** (PERSONAL_CONTEXT §2). Đây là sự kiện quan trọng nhất kể từ W22: blocker #1 của 4 domains (legal/family/finance/health bandwidth) chính thức được gỡ. Trước đây W25-W26 đoán con số 8-20M unknown → nay KNOWN = 11M. Burn rate tính được: 25M (cá nhân) + 11M = **36M/tháng**. EF gap giờ quantify được: cần 108-216M (3-6 tháng). | legal ↔ family_gg ↔ finance | [`_cases/closed/legal_divorce_court_GG_access.md`](../_cases/closed/legal_divorce_court_GG_access.md) (status CLOSED, QĐ 575); [PERSONAL_CONTEXT §2](../00_CORE_LOGIC/PERSONAL_CONTEXT.md) (child support 11M, từ 10/7); [log.md](../30_KNOWLEDGE_BASE/wiki/log.md) (07/03-07/12: RESOLVED flags); [Daily_Pulse](../10_PULSE/Daily_Pulse.md) (last 06/19, không ghi outcome) | 🔴 Critical gap → **RESOLVED** — W26→W28: **FLIPPED** |
| 2 | **NEW visitation-enforcement case (07/12) — Warren fulfilled support (17.2M > 11M obligation) but Khanh obstructs access; legal frontend re-opens** — Dù QĐ 575 có hiệu lực và Warren đã chuyển 11M (đúng hạn 10/7) + 6.2M học phí GG (tổng 17.2M, vượt thỏa thuận), Khanh nhận tiền nhưng từ chối chốt lịch thăm nom ("đợi thời gian trả lời") + công kích khi hỏi trường học GG. Mục tiêu: gặp GG 1-2 lần/tuần, ưu tiên thỏa thuận (Bước 1 văn bản thiện chí). Legal domain tái mở ở mặt trận MỚI: không còn "outcome unknown" (W26) mà là "enforcement blocked" (W28). Quyền thăm nom theo QĐ 575 bị cản trở thực tế. | legal ↔ family_gg | [`legal_quyen_tham_nom_GG.md`](../_cases/active/legal_quyen_tham_nom_GG.md) (OPEN 07/12, priority high); [PERSONAL_CONTEXT §2](../00_CORE_LOGIC/PERSONAL_CONTEXT.md) (access vẫn blocked); [log.md](../30_KNOWLEDGE_BASE/wiki/log.md) (07/12 case opened) | 🔴 Critical gap — **NEW** (W28) |
| 3 | **Oil collapse ($87→$72) flips PVD/GAS thesis polarity — Sư Tử Trắng 2B catalyst now fights a falling-price tide** — W26 có Brent $87-93 làm tailwind cho PVD/GAS (#4 amplification). W28: Brent xuống $71.94 (W27), UAE khôi phục xuất khẩu dầu → áp lực <$70 (07/04). PVD IV 31k, giá 31.1k (sát IV, -1%); GAS 75.3k vs IV 70k. Tailwind dầu BỊ LOẠI, còn catalyst dài hạn (Sư Tử Trắng 2B từ 2027, FTSE Sep 21, NQ10/MSCI 2030) thì chưa thực. Net: PVD/GAS bớt hấp dẫn near-term. Vẫn 100% cash, vẫn block bởi 0 EF + giờ có thêm 11M/tháng drain. | trading | [021_VNStock_Macro](../10_PULSE/021_VNStock_Macro.md) (07/04 UAE tăng cung; 07/08 GDP 8.18%); [020_VNStock_Weekly_Outlook W27](../10_PULSE/020_VNStock_Weekly_Outlook.md) (Brent $71.94, sideway); [034-PVD/Thesis](../30_KNOWLEDGE_BASE/wiki/03_Investing/VN_Equities/030-Companies/034-PVD/Thesis.md) (IV 31k, giá 31.1k); [031-GAS/Thesis](../30_KNOWLEDGE_BASE/wiki/03_Investing/VN_Equities/030-Companies/031-GAS/Thesis.md) (75.3k vs IV 70k) | 🟡 Contradiction — W26→W28: **TAILWIND REMOVED** |
| 4 | **Watchlist expanded to 9 tickers (VCB, BID, FPT, PNJ added) while 100% cash + 0 EF + new 11M/month drain — opportunity cost widens as research depth grows** — W26 chỉ có PVD là clean signal. W28: 9 candidates (GAS, NLG, PVD, HPG, MWG, PNJ, FPT, VCB, BID), tất cả YELLOW/RED (không mã nào rẻ hơn IV trừ PVD sát). FPT stock-deploy 95/100 "bắn" nhưng giá 72.9k vs IV 90-95k (+18-25% upside). Research engine sinh thêm nhiều targets trong khi vốn vẫn 100% sideline. Child support 11M/tháng mới làm EF build chậm hơn. Mở rộng nghiên cứu ≠ proximity to entry. | trading ↔ finance | [Candidates_Watchlist](../30_KNOWLEDGE_BASE/wiki/03_Investing/VN_Equities/Candidates_Watchlist.md) (9 tickers, last_updated 07/13); [020_VNStock_Weekly_Outlook](../10_PULSE/020_VNStock_Weekly_Outlook.md) (100% cash, "chưa có entry point"); [PERSONAL_CONTEXT §11E](../00_CORE_LOGIC/PERSONAL_CONTEXT.md) (0 EF) | 🟡 Contradiction — W26→W28: **WIDENING** |
| 5 | **Weight 61kg now a STABLE 19-day baseline (06/24–07/12), not an anomaly — health data disciplined via Sleep_Log while Daily_Pulse still 23-day gap + 050_Health_Log 42-day gap** — W26 flag weight 61kg là "drop 2kg anomaly". W28 xác nhận: 61kg consistent từ 06/24 qua 07/12 (19 entries Sleep_Log), fasting 18h stable, sleep quality avg ~89 (excellent). → 61kg là NEW stable baseline, không phải anomaly. NHƯNG: 050_Health_Log untouched từ 06/01 (42 ngày) → LDL 4.50/ApoB 120 intervention VẪN thiếu. Daily_Pulse last 06/19 (23-day gap). Meta: capture discipline cải thiện chọn lọc (chỉ Sleep_Log), không toàn diện. | health ↔ meta | [051_Sleep_Log](../10_PULSE/051_Sleep_Log.md) (61kg 06/24-07/12, 19 entries; 07/12 = 90 quality); [050_Health_Log](../10_PULSE/050_Health_Log.md) (last_updated 06/01, LDL/ApoB unaddressed); [Daily_Pulse](../10_PULSE/Daily_Pulse.md) (last 06/19); [log.md](../30_KNOWLEDGE_BASE/wiki/log.md) (07/12: Daily_Pulse gap 23 ngày) | 🟡 Correlation — W26→W28: **CONFIRMED STABLE** |

**📊 Stats:** 5 connections | 6 domains involved (legal, family_gg, finance, trading, health, meta)

**🔗 Most connected domain:** legal ↔ family_gg ↔ finance ↔ trading (each appears in 2 of 5 connections)

**🔄 Previous week (W26) comparison:**
| Connection | W26 status | W28 change |
|---|---|---|
| #1 (legal mediation outcome unknown) | 🔴 Critical gap | **RESOLVED** — QĐ 575 (07/03) defines 11M/month support, visa rights. 16-day gap closed. |
| #2 (weight 61kg drop + BP anomaly) | 🟡 Correlation | **CONFIRMED STABLE** — 61kg = new baseline (19d), not anomaly; LDL/ApoB still unaddressed (42d gap) |
| #3 (catalysts stacking vs blocked capital) | 🟡 Contradiction | **TAILWIND REMOVED** — oil $87→$72 kills PVD/GAS near-term edge; FTSE/NQ10 still long-term |
| #4 (PVD clean entry signal) | 🟢 Amplification | **WIDENING** — watchlist 9 tickers, all YELLOW/RED; still 100% cash, new 11M drain |
| #5 (capture discipline partial) | 🟡 Correlation | **SELECTIVE PERSISTS** — Sleep_Log 19d excellent, Daily_Pulse 23d gap + 050_Health_Log 42d gap |

**💡 Feed into /personal-context-update (Monday):**
1. **[HIGH] Court RESOLVED 07/03 (QĐ 575) — child support 11M/month from 10/7.** Burn = 25M + 11M = 36M. EF gap now quantifiable: 108-216M (3-6mo). Top financial planning priority.
2. **[HIGH] NEW visitation-enforcement case (07/12) — Warren paid 17.2M (vượt 11M), Khanh obstructs.** Legal frontend reopened. Keep paying, build evidence (screenshot, biên lai).
3. **[MOD] Oil fell to $72 — PVD/GAS thesis tailwind weakened.** Recheck entry calculus; still 100% cash, 0 EF. FPT cheapest (% upside) but all below IV.
4. **[MOD] Health: 61kg = new stable baseline; LDL/ApoB intervention STILL missing 42 days.** 050_Health_Log untouched since 06/01. Book repeat lipid panel (target 09/2026).
5. **[MOD] Capture discipline: Sleep_Log excellent (19d), but Daily_Pulse 23-day gap + 050_Health_Log 42-day gap.** Backfill or accept Sleep_Log as primary health pulse.

---

## 2026-W26 (22/06–28/06)

| # | Connection | Domains | Evidence | Signal |
|---|---|---|---|---|
| 1 | **Court mediation outcome unknown (+12 days post-session) — structural paralysis across 4 domains, longest data gap in vault** — Phiên tòa hòa giải ngày 17/06 đã qua. **12 ngày không có update.** follow_up reset lên 28/06 (hôm nay) vẫn critical gap. Case file pre-mortem (13/06) chi tiết đến từng script đàm phán — nhưng **không biết kết quả thực tế**. Outcome trực tiếp block: GG access path, child support amount (8-20M chưa biết con số nào), monthly burn calculation (25M → có thể +13M = 38M), EF timeline (0 tháng gốc + thêm gánh nặng). Không chỉ là legal gap — nó paralyze toàn bộ financial planning cá nhân. | legal ↔ family_gg ↔ health ↔ meta | [`_cases/active/legal_divorce_court_GG_access.md`](../_cases/active/legal_divorce_court_GG_access.md) (follow_up=28/06, last substantive update Jun 13 pre-session); [Daily_Pulse](../10_PULSE/Daily_Pulse.md) (last entry Jun 19, mentions court Jun 17 with no outcome); [log.md](../30_KNOWLEDGE_BASE/wiki/log.md) (Jun 27-28 daily flags) | 🔴 Critical gap — W25→W26: **PERSISTS** |
| 2 | **Weight dropped 2kg (63→61kg) + BP 107/66 anomaly, while LDL/ApoB still unaddressed — health signals diverging without intervention** — Sleep log shows weight **61kg consistent from Jun 24 onward** (5 ngày liên tiếp), sau nhiều tuần ổn định 63kg. BP Jun 28: 107/66 systolic cao hơn baseline (95-99). Fasting tăng từ 17h lên 18h consistent — có thể giải thích weight drop một phần. Nhưng LDL 4.50 / ApoB 120 từ panel Jun 11 vẫn chưa có dietary intervention logged. Sleep avg ~7h35, quality ~88.6 — tốt hơn W25. Paradox: **sleep improving, weight dropping, but blood chemistry worsening.** | health | [051_Sleep_Log](../10_PULSE/051_Sleep_Log.md) (Jun 22-28 entries: weight 61kg from Jun 24, BP 107/66 Jun 28); [050_Health_Log](../10_PULSE/050_Health_Log.md) (last_updated Jun 1, no new entries) | 🟡 Correlation — NEW |
| 3 | **MSCI keeps VN at Frontier, FTSE Sep 2026 upgrade confirmed — catalysts stacking intensely but capital deployment still blocked by 0-month EF + pending child support** — MSCI review Jun 24: VN stays Frontier (expected, 10/18 tiêu chí). **FTSE EM secondary upgrade confirmed Sep 21, 2026** (~2 tỷ USD passive flows, 4 đợt). LDR easing (TT 25/2026 hiệu lực Jul 1 — room tín dụng mới cho BID/VCB/CTG). TOD railway 171,300 tỷ (trình QH Aug 2026). Sư Tử Trắng 2B (1.2 tỷ m³ khí/năm từ 2027). Dầu Brent $87-93. Watchlist: PVD at IV, MWG Q1 run-rate 11,030 tỷ (+78%), NLG/GAS -11-13% dưới IV. **Nhưng:** 0-month EF + pending child support amount (8-20M unknown) = capital deployment blocked. **Opportunity cost intensifying as catalysts multiply.** | trading | [021_VNStock_Macro](../10_PULSE/021_VNStock_Macro.md) (MSCI Jun 24: VN stays Frontier; FTSE Sep 21 upgrade; LDR easing Jun 23; Sư Tử Trắng 2B Jun 23); [020_VNStock_Weekly_Outlook](../10_PULSE/020_VNStock_Weekly_Outlook.md) (VN-Index 1,830 +2.2% WoW); [Candidates_Watchlist](../30_KNOWLEDGE_BASE/wiki/03_Investing/VN_Equities/Candidates_Watchlist.md) (all YELLOW, PVD closest to IV); 
| 4 | **PVD cleanest entry signal on watchlist — Sư Tử Trắng 2B + oil >$87 + MSCI/FTSE tailwind — but at IV with no margin of safety** — PVD: GREEN (0/6 flags), Deloitte. EPS 1,868. Giá 31,600 sát IV ~31,000 (-1%). Sư Tử Trắng Phase 2B signed Jun 19 cung cấp 1.2 tỷ m³ khí/năm từ 2027 — catalyst dài hạn. Oil Brent $87-93 supportive. Forward P/E 12.5x hấp dẫn. MSCI/FTSE bluechip rising tide hỗ trợ. **Nhưng:** FCF -600 tỷ (capex peak), price at IV = không có margin of safety. Entry <28k mới có MOS. Vẫn chờ. | trading | [Thesis/PVD](../30_KNOWLEDGE_BASE/wiki/03_Investing/VN_Equities/030-Companies/034-PVD/Thesis.md) (GREEN 0/6, EPS 1,868, IV 31k, FCF -600); [021_VNStock_Macro](../10_PULSE/021_VNStock_Macro.md) (Sư Tử Trắng 2B, oil $87-93, FTSE tailwind) | 🟢 Amplification — W25→W26: **PERSISTS** |
| 5 | **Capture discipline partial recovery — sleep log maintained daily (7 entries, W26), but Daily_Pulse still 9-day gap, critical legal outcome unrecorded** — Warren maintained 051_Sleep_Log daily Jun 21-28: 7 entries, consistent. **Đây là cải thiện — W25 hoàn toàn 0 entries trong daily pulse, W26 có sleep tracking.** Nhưng: Daily_Pulse last Jun 19 (9-day gap). Inbox đã cleared (auto-processed dọn sạch). Legal case outcome — single most important event of June — still missing. log.md: mỗi cron đều flag legal gap. Capture discipline đang phục hồi không đều: sleep được, còn lại thì không. | meta | [051_Sleep_Log](../10_PULSE/051_Sleep_Log.md) (7 entries Jun 22-28); [Daily_Pulse](../10_PULSE/Daily_Pulse.md) (last entry Jun 19); [`_inbox/01_unprocessed/`](../_inbox/01_unprocessed/) (empty); [log.md](../30_KNOWLEDGE_BASE/wiki/log.md) (Jun 22-28: repeated critical gap flags) | 🟡 Correlation — W25→W26: **PARTIALLY IMPROVED** |

**📊 Stats:** 5 connections | 5 domains involved (legal, family_gg, health, trading, meta)


**🔄 Previous week (W25) comparison:**
| Connection | W25 status | W26 change |
|---|---|---|
| #1 (legal mediation outcome unknown) | 🔴 Critical gap | **PERSISTS + 12 days** — unchanged, longest gap in vault |
| #2 (LDL worsening trend) | 🟡 Correlation | **SUPERSEDED** — replaced by weight drop + BP anomaly, LDL still unaddressed |
| #3 (market entry zone vs blocked capital) | 🟡 Contradiction | **PERSISTS + catalysts intensifying** — MSCI, FTSE, LDR, TOD, Sư Tử Trắng all landing in 1 week |
| #4 (capture discipline broken) | 🟡 Correlation | **PARTIALLY IMPROVED** — sleep tracking resumed but Daily_Pulse still gap |
| #5 (PVD clean entry signal) | 🟢 Amplification | **PERSISTS** — Sư Tử Trắng 2B adds catalyst |

**💡 Feed into /personal-context-update (Monday):**
1. **[HIGH] Legal outcome still missing — 12 days post-court.** Highest priority. Every domain affected. Single question Warren needs to answer: kết quả phiên 17/6 thế nào? (amount, schedule, next steps).
2. **[MOD] Weight 61kg trend + BP 107/66 — health anomaly vs normal variation.** 2kg drop in 3-4 days needs monitoring. LDL/ApoB still pending intervention.
3. **[MOD] Catalysts intensifying while capital blocked — FTSE Sep 21 upgrade now confirmed.** Entry window clarity improving but structural constraint (0 EF + child support) unresolved. PVD entry <28k remains best candidate.

---

## 2026-W25 (15/06–21/06)

| # | Connection | Domains | Evidence | Signal |
|---|---|---|---|---|
| 1 | **Legal mediation Jun 17 — outcome unknown, single biggest cross-domain event** — Jun 17 court session (GG access + child support) was the most consequential event of the week. No post-17/06 update in case file, no Daily_Pulse since Jun 11. Outcome unknown directly blocks: GG access path, financial planning (child support amount), health bandwidth (stress impact). | legal ↔ family_gg ↔ health | [`_cases/active/legal_divorce_court_GG_access.md`](../_cases/active/legal_divorce_court_GG_access.md) (follow_up=17/06, no update); [Daily_Pulse](../10_PULSE/Daily_Pulse.md) (last entry Jun 11) | 🔴 Critical gap |
| 2 | **LDL worsening trend (4.17→3.49→4.50) across 2026: health data captured, action missing** — Jun 11 lab confirms LDL 4.50 (HIGH), ApoB 120 > 100 target, Chol 6.27. Genetic poor fat metabolism (APOA5/PPARG). Mitigating: CRP 0.51 (no inflammation). Meanwhile physical health excellent (sleep avg 7.57h, quality 88.7, BP 97-99/71-72, weight 63kg stable, 17h fasting consistent). Contrast: blood chemistry deteriorating while physical metrics superb. | health | [050_Health_Log](../10_PULSE/050_Health_Log.md) (Jun 11 panel); [051_Sleep_Log](../10_PULSE/051_Sleep_Log.md) (Jun 15-20 entries) | 🟡 Correlation |
| 3 | **Market drops to 1,792 while LDR easing + TOD railway open new entry paths — but capital still blocked** — VN-Index -2.6% WoW to 1,792, getting closer to TCBS base scenario 1,820-1,880. LDR easing (85%→95%) supports banks (BID, VCB, CTG). TOD railway (171,300 tỷ) supports NLG (Cần Thơ land bank, P/B 0.67) and VHM. Oil easing (Brent -6% to $87) improves GAS entry calculus. BUT: 0-month EF + pending child support = capital deployment blocked. Opportunity cost vs structural constraint unresolved. | trading | [020_VNStock_Weekly_Outlook W25](../10_PULSE/020_VNStock_Weekly_Outlook.md) (VN-Index 1,792, -2.6% WoW); [021_VNStock_Macro](../10_PULSE/021_VNStock_Macro.md) (LDR + TOD Jun 21); 
| 4 | **Capture discipline broken since legal intensification — 11-day Daily_Pulse gap + 5 unprocessed inbox items** — Daily_Pulse not updated since Jun 11 (11 days). 5 items in `_inbox/01_unprocessed/` (3 health logs Jun 17-19, 1 GG visit Jun 9, 1 legal case start Jun 9). Sleep data (Jun 15-20) manually logged in 051 but never backfilled to Daily_Pulse. Legal mediation Jun 17 likely consumed all mental bandwidth. | meta | [Daily_Pulse](../10_PULSE/Daily_Pulse.md) (last entry Jun 11); `_inbox/01_unprocessed/` (5 items pending); [051_Sleep_Log](../10_PULSE/051_Sleep_Log.md) (entries Jun 15-20 present) | 🟡 Correlation |
| 5 | **PVD emerges as cleanest entry signal on watchlist — OPEC+ discipline + Saudi rig migration** — PVD: GREEN (0/6), Deloitte, IV ~31,000, price at IV (30,750). OPEC+ supply discipline + Saudi Aramco draining rigs from SEA → day rate support. Fed cutting cycle reduces USD borrowing costs (150-180bps). PVD is the only ticker at/below IV on the watchlist, unlike GAS (80k vs IV 70k) and NLG (YELLOW, straddling IV). | trading | [log.md](../30_KNOWLEDGE_BASE/wiki/log.md) (Jun 8 PVD ingest); [021_VNStock_Macro Jun 8](../10_PULSE/021_VNStock_Macro.md) (PVD TCBS report); [020_VNStock_W25](../10_PULSE/020_VNStock_Weekly_Outlook.md) (strategy: prioritize cash-rich, low-debt stocks) | 🟢 Amplification |

5 domains involved (legal, family_gg, health, trading, meta)


**🔄 Previous week (W24) comparison:**
| Connection | W24 status | W25 change |
|---|---|---|
| #1 (sleep-market stress) | 🟡 Active | DISSIPATED — sleep stable (avg 88.7) despite deeper market drop (-2.6%) |
| #2 (Mẹ surgery + costs) | 🔴 Active | RESOLVED — replaced by own bloodwork + legal mediation |
| #3 (GG grade 1 + access) | 🔴 Active | PENDING — legal mediation Jun 17 outcome unknown, GG visit Jun 9 positive |
| #4 (health tracking gaps) | 🟢 Amplification | **WORSENED** — capture discipline broken since legal event |
| #5 (cash + no EF) | 🟡 Contradiction | **PERSISTS + COMPOUNDED** — child support unknown adds to capital constraint |

**💡 Feed into /personal-context-update (Monday):**
1. **[HIGH] Missing legal mediation outcome** — single highest priority data gap. No post-17/06 update anywhere. Affects all domains except health.
2. **[HIGH] LDL/ApoB worsening trend** — needs dietary intervention (saturated fat cut), repeat lipid panel Sep 2026. CRP low = mitigating but not an excuse.
3. **[MOD] Capture discipline recovery** — backfill Daily_Pulse (11-day gap), process 5 inbox items. Legal ≠ excuse for losing health/meta tracking.

---

## 2026-W24 (01/06–07/06)

| # | Connection | Domains | Evidence | Signal |
|---|---|---|---|---|
| 1 | Sleep quality drop to 83 on Jun 4 coincided with VN-Index selloff to 1,798 mid-week — market stress may be fragmenting rest | health ↔ trading | [051_Sleep_Log](../10_PULSE/051_Sleep_Log.md) 04/06 (6h, quality 83); [020_VNStock_Weekly_Outlook](../10_PULSE/020_VNStock_Weekly_Outlook.md) W23 (selloff 1,798, RSI 44.4) | Correlation |
| 2 | Mẹ eye surgery cost (2M+) + 0-month emergency fund + 25M/month burn = health events directly threaten financial runway | health ↔ family_gg | [Daily_Pulse](../10_PULSE/Daily_Pulse.md) 24–29/05 (surgery + costs); [TODO_Kanban](../TODO_Kanban.md) (overdue Mẹ follow-up) | Correlation |
| 3 | GG grade 1 entry Sept 2026 colliding with blocked access + no custody agreement — timeline pressure building | family_gg | [002_GG_Milestones](../10_PULSE/002_GG_Milestones.md) (Lê Đình Chinh Sept); [PERSONAL_CONTEXT.md §2](../00_CORE_LOGIC/PERSONAL_CONTEXT.md) (access blocked); [Daily_Pulse 04/06](../10_PULSE/Daily_Pulse.md) (visited school) | Correlation |
| 4 | Personal Doctor system created Jun 2 but health tracking still fragmented — sleep logged, baseline TODOs remain | health ↔ meta | [051_Sleep_Log](../10_PULSE/051_Sleep_Log.md) (data present); [000_Bloodwork_Health_Baseline](../30_KNOWLEDGE_BASE/wiki/02_Health/aa_Bloodwork_Health_Baseline/000_Bloodwork_Health_Baseline.md) (workout/RHR TODOs) | Amplification |
| 5 | 100% cash + NLG/GAS both YELLOW (-11%/-13% below intrinsic) = opportunity cost vs emergency fund gap unresolved | trading | [Candidates_Watchlist](../30_KNOWLEDGE_BASE/wiki/03_Investing/VN_Equities/Candidates_Watchlist.md) (NLG 26k vs IV 23k, GAS 79.9k vs IV 70k); [STOCK_CONTEXT.md §3](../00_CORE_LOGIC/STOCK_CONTEXT.md) (100% cash, 0 EF) | Contradiction |

**Stats:** 5 connections | 3 domains involved (health, trading, family_gg)



**🔄 Previous week comparison:** Connections #2, #3, #5 continue from W23. Week 2 — becoming a pattern: emergency fund tension and GG grade 1 prep are persistent structural themes.

**💡 Feed into /personal-context-update (Monday):**
- Connection #1 (sleep-market stress correlation) — new, actionable: review screen-time before bed during volatile weeks
- Connection #2 (health costs + no EF) — Week 2 pattern, most impactful structural constraint
- Connection #3 (GG grade 1 + access) — Week 2 pattern, Sept 2026 deadline approaching
- Connection #5 (cash + watchlist + no EF) — Week 2 pattern, capital deployment blocked by same constraint

---

## 2026-W23 (01/06–07/06)

| # | Connection | Domains | Evidence | Signal |
|---|---|---|---|---|
| 1 | Emergency fund 0 months creates cross-domain tension — blocks trading entry, limits parent health support capacity, strains monthly burn | trading ↔ health ↔ family_gg | [HOME.md](../00_CORE_LOGIC/HOME.md#-red-flag-monitor) 🔴 active flag; [Daily_Pulse](../10_PULSE/Daily_Pulse.md) 24/5 & 28/5 (2M for Mẹ surgery); [Candidates_Watchlist](../30_KNOWLEDGE_BASE/wiki/trading/VN_Equities/Candidates_Watchlist.md) (NLG CLEAN, entry research queue) | 🔴 Correlation |
| 2 | GG asking about separation (23/5) + grade 1 entry Sept 2026 + access blocked — developmental milestone colliding with unresolved family situation | family_gg | [Daily_Pulse 23/5](../10_PULSE/Daily_Pulse.md#2026-05-23) (GG: "sao 2024 ba ko về nhà"); [GG_Communication_Guide](../10_PULSE/001_GG_Communication_Guide.md) (consistent answer ready); [PERSONAL_CONTEXT.md §2](../00_CORE_LOGIC/PERSONAL_CONTEXT.md#2-family-status) (access blocked, no custody agreement); [002_GG_Milestones 27/5](../10_PULSE/002_GG_Milestones.md) (Lê Đình Chinh Sept); [_ideas/2026-05](../_ideas/2026-05.md) (grade 1 profile) | 🔴 Correlation |
| 3 | Mẹ eye surgery successful but out-of-pocket costs (2M+) + materials insurance gap — financial pressure directly impacting family health support | health ↔ family_gg | [Daily_Pulse 24–29/5](../10_PULSE/Daily_Pulse.md) (surgery progression + costs); [TODO_Kanban.md](../TODO_Kanban.md) (follow-up calendar events); [HOME](../00_CORE_LOGIC/HOME.md#-health--latest) (Mẹ eye surgery recovery 🟡) | 🟡 Causality hint |
| 4 | Health data gap persists — Daily Pulse health bullets empty, sleep/workout not tracked — but Personal Doctor system created same day to address it | health ↔ meta | [Daily_Pulse](../10_PULSE/Daily_Pulse.md) (23–29/5: health bullets empty except Mẹ updates); [HOME](../00_CORE_LOGIC/HOME.md#-health--latest) ("chưa log gần đây"); [050_Health_Log](../10_PULSE/050_Health_Log.md) (last lab March 2026) | 🟢 Amplification |
| 5 | 100% cash position + no emergency fund = zero capital income, amplifying all other financial pressure points | trading | [HOME](../00_CORE_LOGIC/HOME.md#-money--snapshot) (0 equity, 0 emergency fund); [020_VNStock_Weekly_Outlook W22](../10_PULSE/020_VNStock_Weekly_Outlook.md#2026-w22) (100% cash, waiting); [Candidates_Watchlist](../30_KNOWLEDGE_BASE/wiki/trading/VN_Equities/Candidates_Watchlist.md) (entry research active but no capital deployed yet) | 🟡 Contradiction |

**📊 Stats:** 5 connections | 4 domains involved (family_gg, health, trading)



**🔄 Previous week comparison:** First real run — W22 was a placeholder. No continuing patterns to flag yet.

**💡 Feed into /personal-context-update (Monday):**
- Connection #1 (emergency fund cross-domain tension) — the most impactful structural constraint affecting 4 domains
- Connection #2 (GG grade 1 + access blocked) — time-sensitive: entry is Sept 2026, legal/custody path unclear

---

## 2026-W22 (25/05–31/05)

| # | Connection | Domains | Evidence | Signal |
|---|---|---|---|---|
| 1 | Mother's eye surgery recovery tracking alongside financial planning — surgery cost 2M, insurance missing parts, future medical needs vs 25M/month burn | health | [Daily_Pulse](../10_PULSE/Daily_Pulse.md) 24-29 May | 🔴 Correlation |
| 2 | GG processing separation at age 6 (school transition) — questions about "why dad doesn't come home" while preparing for grade 1 entry | parenting | [Daily_Pulse](../10_PULSE/Daily_Pulse.md) 23 May, [PERSONAL_CONTEXT §2](../00_CORE_LOGIC/PERSONAL_CONTEXT.md) | 🟡 Causality |
| 3 | BTC buy target ($55K) on watch while portfolio is 100% cash — opportunity cost of waiting vs emergency fund gap (0 months) | trading | [STOCK_CONTEXT §3](../00_CORE_LOGIC/STOCK_CONTEXT.md) | 🟢 Amplification |
| 4 | No equity positions + 100% cash = time for NLG thesis completion. Market accumulating at 1,820-1,920 range. GAS waiting for <70K | trading | [021_VNStock_Macro](../10_PULSE/021_VNStock_Macro.md) | 🟡 Causality |

**Stats:** 4 connections | 4 domains involved
**Most connected domain:** health
**Feed into Monday's /personal-context-update:** Connection #1 (health costs + financial planning) and #2 (GG school prep + separation conversation) should stay as active themes.

---

> **Purpose:** Rolling log of cross-domain connections found each Sunday by `/personal-weekly-connections`.
> **Newest on top.** Each entry = 1 week.
> **Complement:** Fed into `/personal-context-update` on Monday morning.
