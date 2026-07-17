---
created: 2026-06-17
title: BẢNG CHEAT SHEET CHỈ 1 TRANG — Dành cho người non-IT
domain: meta
type: reference
status: active
last_updated: 2026-06-17
---

# BẢNG CHEAT SHEET CHỈ 1 TRANG

> Mục đích: Bạn **không cần nhớ** bất cứ tên skill nào. Chỉ cần 1 thao tác duy nhất.

---

## QUY TẮC VÀNG (CHỈ 1 DÒNG)

> **MỖI LẦN** bắt đầu làm việc với code/script/parser → gõ:
> ```
> /skill using-agent-skills
> ```
> → rồi nói bình thường tiếng Việt có dấu. AI tự chọn đúng quy trình phù hợp.

---

## VÍ DỤ THỰC TẾ

### 1. Sửa script đang lỗi
```
/skill using-agent-skills
```
→ *"Script fetch_broker_reports.py bị lỗi khi parse PDF, nó trả về entry trống. Hãy sửa lại."*

### 2. Thêm chức năng mới
```
/skill using-agent-skills
```
→ *"Tôi muốn thêm chức năng gửi weekly outlook qua Telegram tự động."*

### 3. Fix bug nhỏ
```
/skill using-agent-skills
```
→ *"Template weekly bị ghi đè, phải append sau chứ không phải ghi đè lên."*

### 4. Xem code có vấn đề gì không
```
/skill using-agent-skills
```
→ *"Review giùm script này xem có rủi ro gì không trước khi tôi push."*

---

## NẾU AI LÀM SAI, BẠN NHÉT NÓ VÀO ĐÚNG TRACK BẰNG CÁCH NÓI:

| Bạn muốn... | Nói thêm... |
|-------------|-------------|
| Code có test đảm bảo | *"Phải có test chạy đúng trước khi xong"* |
| Làm từ từ, từng bước | *"Chia làm từng slice nhỏ, mỗi bước đều test/build pass rồi mới next"* |
| Làm gọn code rối | *"Refactor cho dễ đọc, giữ nguyên chức năng"* |
| Đảm bảo không có lỗ bảo mật | *"Kiểm tra bảo mật trước khi đẩy"* |
| Kiểm tra lại trước khi tin | *"Review kỹ rồi mình mới approve"* |

---

## TẠI SAO CHỈ CẦN 1 DÒNG?

`using-agent-skills` là **skill tổng** — nó đọc tình huống của bạn, rồi tự động:
- Phân tích xem đang làm gì (sửa bug? thêm feature? review code?)
- Tự chọn đúng skill con phù hợp
- Áp dụng đúng checklist, quy trình của senior engineer

Bạn **không cần** nhớ:
- spec-driven-development
- incremental-implementation
- test-driven-development
- code-review-and-quality
- debugging-and-error-recovery
- planning-and-task-breakdown
- ...

Chỉ cần **1 dòng** bật cổng, AI lo phần còn lại.

---

## NẾU BẠN QUÊN MẤT, HỎI AI BẰNG CÁCH NÓI:

*"Tôi đang làm gì với code/script, workflow đúng là gì?"*

AI sẽ tự recall và chỉ cho bạn đúng workflow tiếp theo.

---

## LƯU Ý CHO NGƯỜI NON-IT

1. **Không code 1000 dòng rồi mới test** — AI đã được dạy "code từng bước nhỏ, test ngay"
2. **Không tin AI 100%** — dùng `/skill code-review-and-quality` để kiểm tra lại
3. **Bug thì đừng sửa bừa** — dùng `/skill debugging-and-error-recovery` để tìm root cause
4. **Push code lên GitHub trước khi chạy thật** — dùng `/skill shipping-and-launch`

---

## TÌM LẠI FILE NÀY KHI CẦN

```
10_PULSE/GUIDE_agent_skills.md
```

---

*Template này rút gọn từ repo `addyosmani/agent-skills` cho người dùng non-IT.*
