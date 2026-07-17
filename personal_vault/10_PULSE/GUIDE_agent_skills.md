# Bộ kỹ năng Agent-Skills — Phiên bản dễ hiểu

> Nguồn: https://github.com/addyosmani/agent-skills  
> Cài đặt: `C:\Users\khoans\AppData\Local\hermes\profiles\personal_profile\skills\`  
> Kích hoạt: dùng lệnh `/skill <tên-skill>` trong Hermes

---

## Tóm tắt nhanh

Bộ này dạy AI coding agent làm việc như một **kỹ sư senior**: có kế hoạch, có test, có kiểm tra chất lượng, không code bừa. Bạn không cần dùng hết mỗi lần — chỉ dùng khi làm việc với code/script/parser.

---

## 1. Tên gốc → Tên Việt hóa + Khi nào dùng

### Nhóm "Định hình yêu cầu"

| Tên gốc | Tên dễ nhớ | Dùng khi nào |
|----------|-------------|--------------|
| `interview-me` | **Phỏng vấn người dùng** | Bạn có ý tưởng mơ hồ, chưa rõ muốn cái gì. AI sẽ hỏi lại để làm rõ. |
| `idea-refine` | **Tinh chỉnh ý tưởng** | Bạn có ý tưởng thô, cần thêm phương án A/B để chọn hướng đi. |
| `spec-driven-development` | **Lập spec trước khi code** | Bạn muốn làm feature mới hoặc thay đổi lớn. AI viết bản mô tả chi tiết trước, bạn duyệt rồi mới code. |
| `context-engineering` | **Tìm đúng ngữ cảnh** | Trước khi sửa code, AI đọc đúng file cần đọc, không load hết cả project vào context. |

### Nhóm "Lập kế hoạch"

| Tên gốc | Tên dễ nhớ | Dùng khi nào |
|----------|-------------|--------------|
| `planning-and-task-breakdown` | **Chia nhỏ công việc** | Sau khi có spec, AI chia thành các task nhỏ, verifiable, có thứ tự thực hiện. |

### Nhóm "Code thật"

| Tên gốc | Tên dễ nhớ | Dùng khi nào |
|----------|-------------|--------------|
| `incremental-implementation` | **Code từng bước nhỏ** | Code theo từng slice nhỏ, mỗi bước đều test/build pass rồi mới next. Không code 1000 dòng mới test. |
| `source-driven-development` | **Dựa vào tài liệu chính thức** | Trước khi implement, AI kiểm tra lại doc/spec gốc để đảm bảo không hiểu sai. |
| `doubt-driven-development` | **Hoài nghi chuyên sâu** | Khi quyết định quan trọng/không rõ ràng, AI tự đặt câu hỏi phản biện trước khi implement. |
| `frontend-ui-engineering` | **Làm UI/UX** | Dùng riêng khi bạn đang làm giao diện web/app. |
| `api-and-interface-design` | **Thiết kế API** | Dùng riêng khi bạn đang làm backend/API. |

### Nhóm "Kiểm tra & Sửa lỗi"

| Tên góe | Tên dễ nhớ | Dùng khi nào |
|----------|-------------|--------------|
| `test-driven-development` | **Test trước khi code** | Viết test trước, code sau. Đảm bảo mỗi chức năng đều có test chứng minh nó hoạt động. |
| `browser-testing-with-devtools` | **Test trên trình duyệt** | Dùng thêm khi làm UI: kiểm tra console, network, DOM, screenshot. |
| `debugging-and-error-recovery` | **Tìm và sửa lỗi** | Khi có bug, theo quy trình: tái tạo → định vị → sửa root cause → thêm test guard. |
| `code-review-and-quality` | **Review code** | Trước khi merge/đẩy code, AI review theo 5 trục: đúng logic, dễ đọc, kiến trúc, bảo mật, hiệu năng. |
| `code-simplification` | **Làm gọn code** | Code chạy được nhưng rối, AI refactor cho rõ ràng hơn mà không đổi hành vi. |
| `security-and-hardening` | **Kiểm tra bảo mật** | Review đặc biệt các lỗ hổng OWASP, input validation, secret management. |
| `performance-optimization` | **Tối ưu hiệu năng** | Đo trước, chỉ tối ưu phần thật sự chậm. |

### Nhóm "Đưa lên môi trường thật"

| Tên gốc | Tên dễ nhớ | Dùng khi nào |
|----------|-------------|--------------|
| `git-workflow-and-versioning` | **Quản lý git** | Commit atomic, branch strategy, versioning. |
| `ci-cd-and-automation` | **Tự động hóa CI/CD** | Làm pipeline build/test/deploy tự động. |
| `shipping-and-launch` | **Đưa lên production** | Checklist trước khi deploy: test pass, monitor sẵn, rollback plan, feature flag. |
| `observability-and-instrumentation` | **Giám sát & Logging** | Thêm log, metric, alert cho hệ thống. |
| `documentation-and-adrs` | **Ghi chú & quyết định** | Viết doc, ADR (tại sao làm vậy chứ không phải làm kia). |
| `deprecation-and-migration` | **Ngừng hỗ trợ & di dời** | Khi cần bỏ feature cũ, migrate data sang hệ thống mới. |

---

## 2. Quy trình thực tế theo thứ tự

### Làm feature mới nhỏ (fix bug, thêm chức năng nhỏ)
```
1. spec-driven-development (nếu cần làm rõ yêu cầu)
2. planning-and-task-breakdown (chia nhỏ task)
3. incremental-implementation + test-driven-development (code từng bước, có test)
4. code-review-and-quality (review)
5. git-workflow-and-versioning (commit sạch)
```

### Làm thay đổi lớn (feature mới, refactor lớn)
```
1. interview-me / idea-refine (làm rõ yêu cầu)
2. spec-driven-development (viết spec, bạn duyệt)
3. planning-and-task-breakdown (chia task)
4. incremental-implementation (code từng slice)
5. test-driven-development (test cho từng slice)
6. code-simplification (làm gọn nếu cần)
7. code-review-and-quality (review kỹ)
8. security-and-hardening (nếu liên quan auth/payment)
9. shipping-and-launch (deploy checklist)
```

### Khi có bug
```
1. debugging-and-error-recovery (tái tạo → sửa root cause → thêm regression test)
2. test-driven-development (prove bug fixed)
3. code-review-and-quality (review fix)
```

---

## 3. Cách dùng thực tế

### Kích hoạt skill
- Trong chat Hermes, gõ: `/skill <tên-skill>`
- Ví dụ: `/skill spec-driven-development`
- Sau khi kích hoạt, AI sẽ áp dụng quy trình của skill đó cho các yêu cầu sau.

### Khi nào cần kích hoạt
- **Mới vào buổi làm việc**: `/skill using-agent-skills` (AI tự động chọn đúng skill cho từng yêu cầu)
- **Bắt đầu feature mới**: `/skill spec-driven-development`
- **Code đang bị rối**: `/skill incremental-implementation`
- **Trước khi push code**: `/skill code-review-and-quality`

### Ví dụ thực tế với vault của bạn

#### Ví dụ 1: Sửa script fetch_broker_reports.py
```
/skill incremental-implementation
```
→ rồi nói:  
"Sửa script này để sau khi tải PDF xong, nó tự động parse bằng LLM và điền vào template weekly. Chỉ sửa phần parse, không đổi logic tải PDF."

#### Ví dụ 2: Thêm tính năng mới cho vault
```
/skill spec-driven-development
```
→ rồi nói:  
"Tôi muốn thêm chức năng export weekly outlook ra PDF để gửi cho đội ngũ."

#### Ví dụ 3: Fix bug template insertion
```
/skill debugging-and-error-recovery
```
→ rồi nói:  
"Script insert entry bị lỗi, nó ghi đè lên template block thay vì append sau."

---

## 4. Lưu ý quan trọng cho non-IT

1. **Đừng dùng tất cả skill cùng lúc** — Mỗi skill là một "mũi khoan" cho một việc cụ thể. Dùng đúng việc, đúng lúc.

2. **Spec không cần dài** — 2 dòng cũng được, quan trọng là có "điểm dừng" để bạn duyệt trước khi code.

3. **Test không cần phức tạp** — Chỉ cần có 1-2 dòng chứng minh "code chạy đúng" là đủ.

4. **Mỗi commit là một ý nhỏ** — Không code 10 cái rồi commit 1 lần.

5. **AI không phải lúc nào cũng đúng** — Dùng `code-review-and-quality` để kiểm tra lại trước khi tin.

---

## 5. Tham khảo nhanh

| Bạn muốn... | Dùng skill này |
|-------------|----------------|
| Làm rõ ý tưởng mơ hồ | `interview-me` |
| So sánh nhiều phương án | `idea-refine` |
| Làm feature mới | `spec-driven-development` |
| Chia task nhỏ | `planning-and-task-breakdown` |
| Code từng bước nhỏ | `incremental-implementation` |
| Code có test chạy đúng | `test-driven-development` |
| Review code trước khi đẩy | `code-review-and-quality` |
| Làm gọn code rối | `code-simplification` |
| Tìm và sửa bug | `debugging-and-error-recovery` |
| Đưa lên production | `shipping-and-launch` |

---

*Tài liệu này được tạo từ nội dung thật của repo `addyosmani/agent-skills` và rút gọn cho người dùng non-IT.*
