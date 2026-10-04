# Automation audit findings — telegram capture-sleep pipeline (2026-08-24)

Session: Bố yêu cầu dump toàn bộ code + /review toàn bộ pipeline capture-sleep.
Scope: cron job 200706218440 (`*/2 6-13 * * *`, no_agent) → AppData wrapper
`telegram_capture_sleep_runner.py` → `telegram_health_poller.py --once`
→ parse `[capture-sleep]` → draft Telegram → chờ 'ok'/'skip'
→ vault `051_Sleep_Log.md` + GSheet `W-capture-sleep` + git commit+push.
Method: nguyên văn 6 file + live probes (dry-run parse, normalize_reply,
live `getChatHistory` call) + independent adversarial critic (delegate_task).

Companion file: `references/capture-sleep-root-causes.md` (root causes A-C từ
session debug trước — standalone-ok drop, reply-hidden draft, GSheet SA setup).
File này CHỈ chứa finding mới của audit 24/08.

## D1 — Confirmation-gate bị auto-approve bypass [HIGH]
Hai nhánh tự ghi vault KHÔNG cần 'ok':
- `poll_once()` no-updates branch (~dòng 328-347): pending quá 30 phút
  (`pending_timed_out`) → `write_vault` + `sync_and_commit` ngay lập tức.
- `auto_approve_if_new_message()` (~267-280): bất kỳ tin nhắn sau đó từ Warren
  CHỨA chuỗi ngày (vd "2026-07-25") → coi như đã duyệt pending.
Tin chứa ngày không phải là lời duyệt. Gate thật phải re-ask hoặc drop
proposal hết hạn — không bao giờ tự ghi.

## D2 — Dead fallback vẫn nằm trong code: `getChatHistory` [HIGH]
`scan_chat_history_for_ok()` (~283-319) gọi Bot API method `getChatHistory` —
method KHÔNG tồn tại trong Telegram Bot API. Live test 24/08: HTTP 404 Not Found
→ hàm luôn trả False → cả nhánh fallback chết im lặng.
Root cause A (file companion) đã ghi chú "API 404 — never use it" nhưng code
chưa xóa hàm chết. Lesson: khi sửa fallback, XÓA hoặc THAY thế đường chết;
fallback chết = false sense of safety khi getUpdates queue bị consumer khác ăn.

## D3 — Thông báo thành công gửi TRƯỚC side-effect [MOD-HIGH]
`process_reply` (~243-247): gửi "✅ Đã ghi vault ... + sync GSheet + git push"
TRƯỚC khi `sync_and_commit()` chạy. Commit message gắn cứng
"+ GSheet sync (auto)" dù sync có thể fail ngay sau đó (sync fail chỉ print ra
stdout cron, Bố không thấy trên Telegram). Vi phạm verify-before-claim ở cấp
thiết kế: thông báo phải là kết quả CUỐI sau read-back, không phải lời hứa.

## D4 — .gitignore drift vs tracked files [MOD]
`personal_vault/.gitignore:63` có mẫu `scripts/` NHƯNG `telegram_health_poller.py`,
`telegram_notify.py`, `test_telegram_health_poller.py` vẫn tracked (verify bằng
`git check-ignore -v` + `git ls-files`). File MỚI thêm vào scripts/ sẽ bị im lặng
bỏ khỏi git; script chính của pipeline chỉ sống nhờ từng được track từ trước.

## D5 — Không có lockfile chống chạy chồng [LOW-MOD]
Cron mỗi 2 phút; worst-case 1 cycle (nhiều `tg_api` timeout 15s + subprocess
GSheet 60s×2) có thể vượt 2 phút → 2 poller song song đọc cùng offset/pending.
Fix gợi ý: lockfile (`msvcrt.locking`/`portalocker`) hoặc nới schedule.

## D6 — Vệ sinh nhỏ [LOW]
- Comment mojibake dòng ~192 poller ("đứng独立思考").
- Hardcoded `CHAT_ID` + `VAULT_ROOT` tuyệt đối trong 3 file.
- Wrapper nhân đôi: AppData `profiles/personal_profile/scripts/` +
  vault `automation/telegram_capture_sleep_runner.py` — verify 24/08:
  byte-identical (860 bytes). Nếu sửa 1 bản phải sync bản kia.

## Verified-GOOD (đừng re-flag ở audit sau)
- Dry-run parse đúng format chuẩn, kể cả thiếu BP; `normalize_reply('ok 👍')='ok'`.
- State files sạch khi idle: chỉ `.telegram_offset.json`, không pending treo.
- ACK trước dup-check đúng thiết kế; token bot đọc `.env` ngoài repo, không hardcode.

## Pending cho session foreground (curator turn bị chặn)
SKILL.md của umbrella cần thêm rule class-level sau (gate read-before-write
chặn patch trong background curator turn — xem Tool-lesson):
"When reviewing an automation that waits for user approval, trace EVERY branch
that calls write/sync/send/commit. Approval gates rot into silent bypasses:
timeout auto-approve, any-later-message-containing-X-counts-as-yes. A date
string in a chat is not consent."

## Tool-lesson cho chính Hermes (curator turn, cập nhật memory cũ)
Read-before-write gate của `skill_manage` áp dụng cho CẢ `patch` lẫn
`write_file` trên file skill ĐÃ TỒN TẠI — và `skill_view` trả dedup
(`content_returned:false`) KHÔNG được tính là load. Tên load khác tên ghi
(`debugging/X` vs `X`) cũng bị tính là 2 cặp riêng. Đường thoát đáng tin:
tạo file reference MỚI (chưa tồn tại) — không bị gate; phần sửa SKILL.md /
file cũ để dành session foreground.