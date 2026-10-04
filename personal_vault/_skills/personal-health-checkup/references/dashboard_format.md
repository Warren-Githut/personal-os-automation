# Bloodwork Dashboard Format — HTML/Chart.js

## Yêu cầu chung
- File HTML độc lập, dùng Chart.js CDN
- Dark theme, traffic-light colors (green/yellow/red)
- Responsive, xem được trên desktop và mobile

## Cấu trúc trang
1. **Header** — tên, tuổi, cân nặng, ngày cập nhật, source PDF
2. **Alert Banner** — cảnh báo nếu thiếu dữ liệu hoặc có bất thường
3. **Summary Cards** — cards với màu traffic-light + trend arrows (↑/↓/→)
4. **Category Tabs** — filter theo nhóm chỉ số (Đường huyết, Mỡ máu, Gan, Thận, Viêm, Điện giải, Khác)
5. **Charts** — line chart cho mỗi chỉ số, có target reference lines
6. **Data Table** — bảng tổng hợp theo ngày
7. **Genotype-Phenotype Cross-Reference** — bảng so sánh gen vs thực tế
8. **Recommendations** — khuyến nghị từ personal doctor

## Chart.js Config
- Line chart với tension: 0.3
- Point radius: 5, hover radius: 7
- Target lines: dashed, green (mục tiêu) / red (cảnh báo)
- Tooltip hiện giá trị + đơn vị
- X-axis: ngày (dates array)
- Y-axis: giá trị + đơn vị
- spanGaps: true (nối đường đứt khi null)

## Color Scheme
- Green: #4caf7d (bình thường/tốt)
- Yellow: #e8c84c (cảnh báo/gần ngưỡng)
- Red: #e85d5d (bất thường/cao)
- Orange: #e8955d (phụ)
- Blue: #6c8cff (primary)

## Lưu ý
- Mỗi chart card có data-cat attribute để filter theo tab
- Summary cards có ::before border-top với màu traffic-light
- Lưu file vào `aa_Bloodwork_Health_Baseline/`
