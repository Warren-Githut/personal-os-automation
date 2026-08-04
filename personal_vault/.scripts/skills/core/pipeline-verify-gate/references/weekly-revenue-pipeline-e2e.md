# Weekly Revenue Pipeline — E2E Build/Verify Recipe (2026-07-24)

Concrete learnings từ build `01_weekly_revenue` pipeline (orchestrator + telegram intake + `revenue_screenshot_parser.py` v2.1). Reproduce khi build pipeline OCR tương tự.

## File map (thực tế trên disk — SPEC ghi sai path, verify trước khi tin)
- Orchestrator: `vault/.scripts/run_weekly_revenue_pipeline.py` (MỚI)
- Telegram intake: `vault/.scripts/revweek_telegram_intake.py` (MỚI)
- OCR parser (thợ): `vault/10_OPERATION_DATA/.parsers/revenue_screenshot_parser.py` v2.1
- Dashboard (thợ): `vault/10_OPERATION_DATA/.parsers/gen_revenue_dashboard.py`
- Telegram sender: `vault/.scripts/_send_telegram.py` (token từ `~/AppData/Local/LUsineWorkBot/.env`, chat `2117653672`)
- Git remote: `git@github.com:Warren-Githut/warren-os-lusine.git`
- SPEC ghi parser ở `.scripts/` → SAI, thực tế ở `.parsers/`. Luôn `ls`/`find` verify disk.

## Parser exit-code contract (orchestrator map)
| Exit | Ý nghĩa | Orchestrator → Bố |
|---|---|---|
| 0 | OK, verify pass | gửi template v3 |
| 1 | thiếu args/ảnh | 🔴 THIẾU ẢNH / SAI LỆNH |
| 2 | verify gate FAIL (L1 sum/L2 OCR/L3 internal) | 🔴 VERIFY FAIL (chi tiết stderr) |
| 4 | OCR FAIL (ảnh lỗi/mờ/path sai) | 🔴 OCR FAIL |

Parser v2.1 có built-in `verify_gate`: L1 sum stores==ALL (net_rev+covers), L2 double-parse, L3 internal consistency. Orchestrator KHÔNG re-implement — chỉ map exit code.

## Liteparse path pitfall (CRITICAL)
- OCR FAIL dù file tồn tại → CHECK PATH. MSYS `/c/Users/...` → liteparse nhận `\c\Users\...` → fail.
- Fix: truyền `C:\Users\...` (Windows thuần) khi gọi parser từ orchestrator.
- Test trực tiếp: `python revenue_screenshot_parser.py --sys "C:\..." ...` (OK) vs qua orchestrator path `/c/...` (FAIL).

## E2E thực tế (ảnh thật Warren gửi)
1. Copy 4 ảnh vào temp: `sys.jpg` (System tổng), `lu3/lu5/lu7.jpg`.
2. Dry-run (KHÔNG ghi vault):
   ```
   python run_weekly_revenue_pipeline.py --sys "C:\...sys.jpg" --lu3 "C:\...lu3.jpg" \
     --lu5 "C:\...lu5.jpg" --lu7 "C:\...lu7.jpg" --week 2026-W29 --dry --no-git --no-tg
   ```
3. Nếu OCR drop covers → dùng `--override-json` có đủ keys:
   ```json
   {"SYS":{"covers":2583,"avg":265022,"tickets":2000},
    "LU3":{"covers":926,"avg":262430,"tickets":709},
    "LU5":{"covers":735,"avg":269163,"tickets":614},
    "LU7":{"covers":922,"avg":264322,"tickets":677}}
   ```
   Override handler phải accept `covers`+`avg` (không chỉ net_rev/tickets).
4. Verify: EXIT 0 + SSOT `grep -c "^## 2026-W29"` vẫn =1 (dry không ghi) + `git status` clean.

## OCR layout bug (đã fix trong parser)
- `_primary_metric_row`: lấy `lines[-1]` trước dòng label "NET REVENUE" (KHÔNG `full_text[:m.start()].splitlines()[-1]` — dễ trúng header date row).
- Ảnh thật: covers (926) nằm giữa net_rev và avg → OCR bỏ sót → covers=avg(262430) → verify SUM mismatch bắt được.

## Telegram intake (persist-partial)
- Poll `*/30 8-17 * * 1` (T2 only), no_agent, free.
- Filter user `2117653672` + caption `01_weekly_revenue`.
- Save ảnh NGAY khi nhận: `raw/revenue_screenshots/{week}_{slot}.png` (slot = số thứ tự). Đếm đủ 4 → gọi orchestrator. KHÔNG buffer file_id chờ 1 batch (Bố gửi rải rác → lost).
- Heartbeat `0 17 * * 1`: nếu tuần đó chưa done → 🔔 nhắc (dedup bằng `.revweek_heartbeat.json`).
- Cron script copy vào `profile/scripts/` (cross-profile guard) + `workdir = vault root`.

## Verify gate (ANCHORS)
- A2: Revenue SSOT = `01_SSOT_01_Weekly_Revenue_Log.md`. L3 reconcile KHÔNG so vs 09_Hourly (01 CHÍNH LÀ SSOT).
- A9: verify independent (parser built-in gate, không circular).
- A10: major output qua reviewer-node (spawn SubAgent fresh context).
- Test mode KHÔNG được chạm vault thật (ép `--dry` + skip dashboard).
