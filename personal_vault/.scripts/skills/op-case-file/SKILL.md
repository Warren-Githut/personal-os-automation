---
name: op-case-file
description: "Tạo hoặc cập nhật case file ops trên Google Drive cho bố. Cấu trúc cố định: TO-DO trước, executive summary, cập nhật theo ngày newest-on-top. Luôn viết cùng core-report-writing. STE100. Use when bố asks update case, thêm to-do, tạo case, hoặc điền bảng TO-DO."
type: workflow
lifecycle: active
---

# Case File for Bố — Structure and Update Rules

Áp dụng cho mọi case file ops (LU3 Closure, LU5 Closing, và case khác).

Luôn dùng skill này cùng **core-report-writing**.
- Skill này: cấu trúc section, thứ tự, bảng TO-DO, quy tắc cập nhật.
- core-report-writing: cách viết EXECUTIVE SUMMARY và entry CẬP NHẬT THEO NGÀY (answer first, tách fact/assumption/recommendation, kết bằng "Bố cần làm gì?").

Viết 100% STE100. Ngôn ngữ của bố.

## Section order (cố định)

0. Header block (ngắn, chỉ các field này):
   - Case name
   - Status (Active / Closed)
   - Owner
   - Created date
   - Last updated date
   - Next follow-up
   - Source
   - Không thêm migration note, tags, frontmatter, auto-status.

1. TO-DO / FOLLOW-UP LIST (luôn đầu tiên)
   - Một bảng. Cột: # | Việc | Người làm | Hạn (DD/MM/YYYY) | Trạng thái | Ngày xong | Ghi chú
   - Trạng thái chỉ dùng: CHƯA LÀM, ĐANG LÀM, XONG, BỎ, CHẶN (nói rõ bị chặn bởi gì trong Ghi chú)
   - Row order cố định theo số. Số mới nhất ở trên. Thêm việc mới = row mới ngay dưới header, số = max hiện tại + 1
   - Không di chuyển hoặc sắp xếp lại row cũ. Chỉ sửa cell status, ngày xong, hạn, ghi chú tại chỗ
   - Mọi việc phải có hạn. Không có thì viết "Chưa có hạn" và ghi chú
   - Không xóa việc đã xong. Đánh XONG + ngày xong
   - Row XONG hoặc BỎ: tô xám toàn bộ cell (#D9D9D9)
   - Người làm không biết = "Chưa rõ". Không đoán

2. EXECUTIVE SUMMARY
   - Viết theo core-report-writing
   - 3–7 câu số. Mở "Tính đến DD/MM/YYYY"
   - Tình trạng, quyết định mới nhất, ngày tiếp theo, rủi ro chính
   - Kết bằng "Bố cần làm gì?"
   - Viết lại toàn bộ mỗi lần cập nhật

3. CẬP NHẬT THEO NGÀY
   - Một sub-heading mỗi lần: "CẬP NHẬT DD/MM/YYYY: <tiêu đề>"
   - NEWEST FIRST. Chèn ngay dưới heading section. Không append xuống cuối
   - Mỗi entry ghi nguồn. Viết theo core-report-writing (fact trước, assumption sau, kết "Bố cần làm gì?")
   - Quote quyết định verbatim khi có

4. NGÀY QUAN TRỌNG
   - Một dòng một ngày. Ghi fixed hoặc tentative

5. BỐI CẢNH
   - Fact ngắn. Có nguồn

6. Các section chủ đề nếu cần (nhân sự, tiền, landlord, tài sản...)
   - Fact + nguồn

7. KHÔNG ĐƯỢC LÀM (nếu có rule cấm)

## Update rules

1. Mỗi lần cập nhật:
   - Thêm entry log mới ngay dưới heading CẬP NHẬT THEO NGÀY (newest on top)
   - Sửa bảng TO-DO tại chỗ
   - Viết lại EXECUTIVE SUMMARY theo core-report-writing
   - Cập nhật header dates
2. Sửa document tại chỗ. Không rebuild. Giữ link.
3. Khi ngày đổi, thay ngày cũ ở mọi nơi ngoài log.
4. Không invent ngày, tên, số. Không biết = "Chưa rõ" hoặc "Chưa có hạn".
5. Mirror mốc ngày quan trọng lên Google Calendar khi bố yêu cầu.
6. Sau khi sửa, đọc lại section đã đổi cho bố.

## Kỹ thuật Google Docs

- Ưu tiên: bố tạo sẵn row trống ngay dưới header bảng TO-DO. Mình chỉ điền cell.
- Số mới = số cao nhất + 1. Row mới luôn dưới header.
- Không xóa nội dung nếu chưa hỏi bố.
- Mỗi insert_text lệch index phía sau. Luôn lấy revisionId mới.
- delete_content trên bảng dễ lỗi. Thử range nhỏ hoặc hỏi bố.
- Version history là cách khôi phục nhanh.

## Calendar (project này)

- Tiêu đề: "Việc [số]: [nội dung] [Tên case]"
- Màu Tangerine (colorId 6). Chỉ dùng trong project này.
- Khi bố nói "việc X xong": đánh XONG, điền ngày xong, tô xám. Nếu số trùng nhiều case thì hỏi case nào trước.

## Closing a case

Khi bố muốn đóng case: làm post-mortem theo quy trình trong skill (hỏi từng câu, ghi bài học, chuyển folder, cập nhật index).

## Khi nào dùng

Bố nói "update case", "thêm to-do", "tạo case", "điền bảng", hoặc liên quan closing / handover / ops case.
