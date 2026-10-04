# Verify evidence retention + shared test recorders (2026-08-24 capture-sleep step 3)

Hai bài học từ phiên hardening lockfile cron capture-sleep. SKILL.md chưa mang được
vào (curator read-before-write gate chặn patch khi skill đã load trước đó trong phiên
review) - nội dung đầy đủ nằm ở đây, gộp vào SKILL.md khi Bố chạy foreground session.

## 1. RETENTION: giữ script verify làm bằng chứng khi Bố yêu cầu

Task brief bước 3 ghi rõ: "script hermes-verify-*.py trong %TEMP%, chạy PASS rồi
GIỮ file làm bằng chứng (không xóa cùng lệnh chạy)".

- Quy tắc mặc định "clean up the temp script after" CHỈ áp dụng khi không có yêu cầu
  giữ bằng chứng.
- Khi brief nói GIỮ: không xóa, và trong báo cáo PHẢI dẫn đúng đường dẫn file evidence
  (vd `%TEMP%\hermes-verify-step3-lock.py`) để Bố kiểm tra được sau này.

## 2. Shared test recorders: reset ở ĐẦU test, đừng dựa cleanup của test trước

Suite poller dùng chung 1 dict `CALLS` qua nhiều test. Hai lỗi đối xứng cùng một gốc:

- False RED: test mới assert "no side effects" (`not CALLS["send"]`) nhưng không reset
  -> dính entry rác từ test TRƯỚC -> suite fail dù poller đúng (đã xảy ra thật,
  16/17 RED đầu tiên).
- False GREEN phụ thuộc thứ tự: thiếu reset thì test chỉ pass vì may mắn đứng sau một
  test có reset (reviewer-node bắt được dạng này ở vòng 1).

Quy tắc cứng: mọi test mới mở đầu bằng
`for k in CALLS: CALLS[k] = []  # reset shared recorder`
đặt ở ĐẦU thân test - không phải ở finally/cleanup cuối.

## 3. Kèm theo: assert tautology khi check mojibake/non-ASCII

`"needle-non-ascii" not in src.encode("unicode_escape").decode()` là HẰNG ĐÚNG -
unicode_escape thoát toàn bộ haystack thành `\uXXXX` nên needle raw CJK không bao giờ
match, dù bug còn nguyên (reviewer xác nhận bằng thực nghiệm: assert vẫn PASS trên
source còn chứa lỗi). Assert falsifiable duy nhất là quét codepoint trực tiếp:
`[ch for ch in src if 0x4E00 <= ord(ch) <= 0x9FFF]`.

## Liên quan

- Ladder xử lý reviewer-node gục hạ tầng (500/524) + quy tắc không bịa findings:
  thuộc `pipeline-verify-gate` (user-owned, cần `hermes curator adopt` trước khi
  patch được) - xem đề xuất trong báo cáo curator phiên 2026-08-24.
