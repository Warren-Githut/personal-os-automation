---
domain: investing
type: reference
status: active
data_status: active
last_updated: 2026-07-05
tags: ["trading", "frameworks"]
---

# Frameworks — Sector & Macro Mental Models

> **1 growing file, newest entry on top.** Moi entry = 1 framework suy luan co the tai su dung.
> **Khong tao file rieng theo chu de** — append vao day, dung WIKI_INDEX de tra cuu.

---

## Template entry (copy khi them moi)

## [YYYY-MM-DD] — [Ten framework]

### Dieu kien kich hoat
> Framework nay apply khi: [mo ta ngan tinh huong]

### Co che
[Chuoi logic: A -> B -> C -> ket qua dau tu]

### Co phieu huong loi
- [Ticker] — [ly do]

### Co phieu chiu thiet
- [Ticker] — [ly do]

### Dieu kien pha vo framework
- [Khi nao logic tren khong con dung]

### Bang chung lich su
- [Vi da qua khu framework nay dung/sai]

---
## 2026-07-12 — Macro: BRENT

### Trigger
- BRENT: 71.94 → 76.01 (+5.7%)

### Cross-sector impact
- Brent tăng → GAS/PVD hưởng lợi (doanh thu ↑), DPM/DCM chi phí ↑

### Chi tiết từng chỉ số
- BRENT: 71.94 → 76.01 (+5.7%)
- DXY: 100.88 → 100.97 (+0.1%)
- USDVND: 26463.0 → 26214.0 (-0.9%)
- VNINDEX: 1862.0 → 1862.0 (+0.0%)
- NHNN_RATE: 4.5 → 4.5 (+0.0%)
- VIBOR_ON: 4.5 → 4.5 (+0.0%)

### Cổ phiếu bị ảnh hưởng
- Brent tăng → GAS/PVD hưởng lợi (doanh thu ↑), DPM/DCM chi phí ↑

<!-- state: Brent=76.01 | DXY=100.97 | USDVND=26214.0 | VNINDEX=1862.0 | NHNN=4.5 | VIBOR=4.5 -->

## 2026-06-24 — Baseline (auto-init)

### Giá trị hiện tại
- Brent: $71.94 | DXY: 100.88 | USD/VND: 26463 (NH bán)
- VN-Index: 1862 | NHNN rate: 4.5% | VIBOR ON: 4.5%

### Nguồn dữ liệu
> VN-Index 1862 — nguồn web [LOW]; Brent/Yahoo [MOD]; USD/VND/bank [MOD]

<!-- state: Brent=71.94 | DXY=100.88 | USDVND=26463.0 | VNINDEX=1862 | NHNN=4.5 | VIBOR=4.5 -->


## 2026-06-01 — Oil_Vietnam_Stocks (Brent tang/giam)

### Dieu kien kich hoat
> Brent bien dong >10% trong 1 quy hoac co su kien dia chinh tri (OPEC, lec vung Vong Cung).

### Co che
`
Brent tang -> Dau vao tang -> GAS (LNG trading): loi nhuan LNG tang nhung margin co the bi nen
           -> PVD, PVC: hop dong tham do khai thac tang -> loi nhuan tang truc tiep
           -> DPM, DCM: chi phi phan bon tang -> margin ep (nhung ho tro gia ban)
Brent giam -> GAS: LNG margin duoc cai thien (dau vao re hon)
           -> PVD, PVC: hop dong giam -> anh huong tieu cuc
           -> DPM, DCM: chi phi giam -> margin duoc cai thien
`

### Co phieu huong loi khi Brent tang
- GAS — doanh thu LNG tang (nhung margin khong bang toll pipeline)
- PVD — drilling hop dong tang

### Co phieu huong loi khi Brent giam
- DPM — chi phi phan bon giam
- GAS — margin LNG duoc cai thien (mua re, ban dat)

### Dieu kien pha vo
- Gia ban khi/phan bon do chinh phu quyet dinh (khong theo thi truong)
- VN khong san xuat dau tho -> tac dong gian tiep

### Bang chung lich su
- Q1/2026: Brent nhe, LNG +90% YoY nhung GAS margin giam 14.8% vs 16.4%
- Q1/2025: Brent on dinh hon, GAS margin 16.4%
