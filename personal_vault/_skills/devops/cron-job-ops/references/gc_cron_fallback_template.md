# GC Cron Fallback — Description Template (copy-paste block)

Dùng khi tạo Google Calendar recurring event làm fallback cho 1 cron (vd item-sales-weekly T2 09:00).
Tạo qua `google_api.py calendar create --recurrence "RRULE:FREQ=WEEKLY;BYDAY=MO;BYHOUR=13;BYMINUTE=0"` (OAuth PRODUCTION persist, KHÔNG re-auth).
Description PHẢI self-contained (chat mới hiểu ngay): lệnh + bước + SSOT path + formula + kill-switch. KHÔNG viết runbook .md riêng.

```
<JOB NAME> WEEKLY — FALLBACK (nếu cron T2 09:00 fail)

Cron '<job_id>' chạy T2 09:00 tự động. Nếu BỐ KHÔNG nhận tin nhắn Telegram 🟢/🔴 lúc 09:00
→ cron failed (thường do VPN tắt hoặc SQL dead). Event này (T2 13:00) là nhắc thủ công fallback.

==================================================
COPY-PASTE NGUYÊN BLOCK SAU VÀO CHAT HERMES:
==================================================

Bố ơi, tới phiên <job> weekly fallback. Cron 09:00 có vẻ fail (không có tin nhắn). Con chạy thủ công nhé:

Làm tuần Wxx (tuần vừa đóng, ví dụ T2 27/07 → W30 = 20-26/07):
1. BỐ bật VPN / đảm bảo <prereq>.
2. Con chạy: <lệnh hermes đầy đủ, ví dụ python vault/.scripts/<parser>.py --live --emit-html vault/.../template.html>
3. Verify: <checklist — tracker có 1 block Wxx, dashboard có </script> đóng, không trắng chart>.
4. Nếu OK → con báo 🟢, BỐ gõ 'ok NN' để con commit+push <files>. KHÔNG tự push (rule 15).
5. Nếu fail → con báo 🔴, BỐ check <prereq> thủ công.

SSOT paths:
- Parser: vault/.scripts/<parser>.py
- Tracker: vault/10_OPERATION_DATA/<tracker>.md
- Dashboard: vault/30_KNOWLEDGE_BASE/wiki/dashboards/<dash>.html (BỐ mở file này, Ctrl+Shift+R nếu cache)
- Template (source, KHÔNG sửa tay): <dash>.template.html

Formulas: <net = gross × 0.882, Rev/Cover, AC...>
Data authority: <SQL IKKO = số chuẩn. KHÔNG sửa tay tracker.>

Kill-switch: BỐ gõ "tắt cron <job>" sẽ pause cron 09:00.

==================================================
HẾT BLOCK — BỐ chỉ cần paste nguyên phần trên vào chat.
==================================================

Sau khi con báo xong → BỐ gõ "ok NN" để con commit push (nếu OK).
```

## Quy trình tạo (proven 2026-07-27)
1. Viết description vào temp file `_gc_<job>_desc.txt` (tránh MSYS escape).
2. `DESC=$(cat _gc_<job>_desc.txt) && python google_api.py calendar create --summary "..." --start "YYYY-MM-DDT13:00:00+07:00" --end "YYYY-MM-DDT14:00:00+07:00" --recurrence "RRULE:FREQ=WEEKLY;BYDAY=MO;BYHOUR=13;BYMINUTE=0" --description "$DESC"`
3. Verify: `calendar list` tuần này (assert start 13:00) + tuần sau (assert event lặp lại).
4. `rm -f _gc_<job>_desc.txt`.

## Pitfalls
- Token: dùng `google_token.json` valid (PRODUCTION persist) — KHÔNG re-auth (cần browser consent Bố).
- `calendar list` JSON KHÔNG hiện field `recurrence` → assert lặp lại bằng list tuần sau.
- Timezone: LUÔN `+07:00` / `Asia/Ho_Chi_Minh`.
