# Codebase Design — Deep Module Vocabulary (Matt Pocock absorb)

> Source: `mattpocock/skills` → `codebase-design` (vocabulary layer chạy dưới `improve-codebase-architecture` + `tdd`).
> Dùng khi viết parser / skill / script mới cho L'Usine vault.

## Tại sao cần (Feynman)
Giống một quán cafe: **module sâu** = cửa trước nhỏ xinh (thực đơn 3 món), nhưng bếp sau rộng, làm được 30 món phức tạp. Khách chỉ cần nhớ 3 món, đầu bếp lo phần khó. **Module nông** = cửa trước treo 30 món, nhưng sau bếp chỉ hâm nóng đồ có sẵn — khách phải nhớ quá nhiều, lợi ích chả bao nhiêu.

## Glossary (dùng đúng từ, không thay thế)
- **Module** — bất cứ gì có interface + implementation (hàm, class, package, pipeline).
- **Interface** — mọi thứ caller phải biết để xài đúng (type signature + invariant + error modes + config + perf). KHÔNG chỉ là "API".
- **Implementation** — cái ở trong module.
- **Depth** — leverage tại interface: nhiều behaviour ẩn sau interface nhỏ = sâu. Interface gần bằng implementation = nông (tránh).
- **Seam** — chỗ có thể đổi behaviour mà KHÔNG sửa tại chỗ đó.
- **Adapter** — concrete thing thỏa mãn interface tại 1 seam.
- **Leverage** — caller được gì từ depth (1 implementation trả nợ qua N call sites + M tests).
- **Locality** — maintainer được gì (fix 1 chỗ = fixed everywhere).

## Nguyên lý
1. **Depth là thuộc tính của interface, không phải implementation.** Module sâu có thể gồm nhiều phần nhỏ mockable bên trong — chúng không nằm trong interface.
2. **Deletion test** — tưởng tượng xóa module. Nếu complexity biến mất → nó chỉ là pass-through (xóa đi). Nếu complexity xuất hiện lại ở N caller → nó đáng giá.
3. **Interface là test surface** — caller và test cùng vượt 1 seam. Muốn test QUA interface → module sai shape.
4. **1 adapter = giả thuyết seam. 2 adapter = seam thật.** Đừng tạo seam nếu không có gì biến thiên qua nó.

## Áp dụng vào L'Usine parser (ví dụ)
- Parser `09_Hourly` nên là module SÂU: interface = `run(week) → SSOT rows`, implementation ẩn logic liteparse + verify + SQL cross-check. Bố chỉ gọi `run(W31)`, không cần biết chi tiết.
- Đừng tạo seam (class tách biệt) cho từng store LU3/LU5/LU7 nếu data shape GIỐNG NHAU → 1 adapter xài chung. Chỉ tách khi store có format khác biệt thật sự.

## Khi nào gọi
- Viết parser/skill mới → design module sâu trước, rồi mới code.
- Review code → chạy deletion test từng module.
- Pair với `improve-codebase-architecture` (#7) + `tdd` (#5) trong quality pipeline.
