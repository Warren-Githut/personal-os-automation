---
name: op-case-file
description: "Cập nhật case LU3 Closure hoặc case vận hành khác trên Google Drive cho bố. Use when bố asks update case, thêm to-do, sửa follow-up, hoặc điền bảng TO-DO trong Google Doc case."
type: workflow
lifecycle: active
---

# Case Update for Bố — LU3 Closure and Ops Cases

Cập nhật Google Doc case trên Drive của bố. Ưu tiên bảng TO-DO / FOLLOW-UP LIST.

## Workflow

1. Tìm case bằng google_drive_search với query "LU3 CLOSURE" hoặc tên case bố đưa.
2. Đọc document bằng cursor__bridge___user-Google-docs-read_5fdocument___16 để lấy table start index và cell indexes.
3. Nếu cần thêm hàng vào bảng TO-DO:
   - **Ưu tiên**: Bố tự tạo row trống ngay dưới header. Mình chỉ điền nội dung vào các cell của row đó.
   - Số mới = số cao nhất hiện tại + 1. Row mới luôn nằm ngay dưới header.
   - Không di chuyển hoặc sắp xếp lại các row cũ.
   - Nếu bố không tạo sẵn: không xóa toàn bộ bảng. Hỏi bố xác nhận trước.
4. Điền cell:
   - Luôn dùng revisionId mới nhất sau mỗi lần insert_text.
   - Điền đúng cột theo header: # | Việc | Người làm | Hạn | Trạng thái | Ngày xong | Ghi chú.
   - Ghi chú dài đặt vào cột Ghi chú, không nhầm sang Ngày xong.
   - Trạng thái chỉ dùng: CHƯA LÀM, ĐANG LÀM, XONG, BỎ, CHẶN.
   - Khi đổi sang XONG hoặc BỎ: ghi ngày xong. Tô xám toàn bộ cell của hàng đó (#D9D9D9). Strikethrough do bố tự làm (tool không hỗ trợ dễ).
   - Re-read sau mỗi vài lần điền để xác nhận index.
5. Cập nhật các mục liên quan (executive summary, ngày quan trọng, cập nhật theo ngày) bằng replace_text hoặc insert_text.
   - Phần "CẬP NHẬT THEO NGÀY": luôn đặt bản cập nhật mới nhất ngay dưới heading section, trên các bản cũ (newest on top).
   - Không append xuống cuối document.
6. Nếu bố yêu cầu Google Calendar trong project này (LU3 / ops case), tạo event bằng google_calendar_create_event. Tiêu đề dạng: “Việc [số]: [nội dung] [Tên case]”. Ví dụ: “Việc 5: Gửi số đếm rượu cho Pang [LU3 Closure]”. Sau khi tạo, set màu Tangerine (colorId 6). Màu này chỉ áp dụng trong project này.
7. Báo lại và xác nhận đã xong.

## Lưu ý kỹ thuật (từ thực tế 10/10/2026)

- **Cấm xóa bất cứ nội dung nào nếu chưa hỏi ý bố.** Nếu tự tin muốn xóa, prompt nhờ bố xác nhận trước.
- Không có tool “insert row vào bảng có sẵn”. Cách an toàn nhất: bố tạo row trống dưới header → mình điền vào cell có sẵn.
- Mỗi insert_text làm lệch toàn bộ index phía sau. Luôn lấy revisionId trả về cho lần tiếp theo.
- delete_content trên range bảng dễ báo lỗi nếu chạm biên cell. Thử range nhỏ hơn nếu cần.
- Version history là cách khôi phục nhanh nhất khi xóa nhầm.
- Khi tạo Google Calendar event/task trong project này: tiêu đề dạng “Việc [số]: [nội dung] [Tên case]”. Ví dụ “Việc 5: Gửi số đếm rượu cho Pang [LU3 Closure]”. Dùng màu Tangerine (colorId 6). Chỉ áp dụng project này.
- Khi cập nhật "CẬP NHẬT THEO NGÀY": insert ngay dưới heading section, newest on top. Không để dưới cùng.

## Khi nào dùng

- Bố nói "update case", "thêm việc to-do", "sửa follow-up", "điền bảng".
- Liên quan LU3 closing, handover, retail clearance, hoặc case ops khác.
