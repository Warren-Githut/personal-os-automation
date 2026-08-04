# Canonical YAML Schemas — 030-Companies Files

Các files trong `investing/VN_Equities/030-Companies/{NUMBER}-{TICKER}/` PHẢI tuân theo schemas dưới đây.

## 1. Thesis.md

```yaml
domain: investing
type: thesis
ticker: MWG
company_name: "Cổ phần Đầu tư Thế Giới Di Động"
sector: Bán lẻ                     # ngành cấp 1
industry: ICT & Điện máy, Bách hóa # ngành cấp 2 (chi tiết)
status: watching | active | archived
last_updated: YYYY-MM-DD
source_files:
  - "filename.pdf (nguồn, ngày)"
tags: [TICKER, sector, theme]
related:
  - "BCTC - Rolling.md"
  - "Anti-thesis.md"
  - "Catalyst-watch.md"
review_log:
  - YYYY-MM-DD: Hành động — mô tả
```

## 2. BCTC - Rolling.md

```yaml
domain: investing
type: bctc
ticker: MWG
company_name: "Cổ phần Đầu tư Thế Giới Di Động"
sector: Bán lẻ
industry: ICT & Điện máy, Bách hóa, Dược phẩm
status: active
last_updated: YYYY-MM-DD
source_files:
  - "nguồn1 (ngày)"
  - "nguồn2 (ngày)"
tags: [TICKER, BCTC, nguồn]
related:
  - "Thesis.md"
  - "Anti-thesis.md"
review_log:
  - YYYY-MM-DD: Hành động — mô tả
```

## 3. Anti-thesis.md

```yaml
domain: investing
type: anti-thesis
ticker: MWG
company_name: "Cổ phần Đầu tư Thế Giới Di Động"
sector: Bán lẻ
industry: ICT & Điện máy, Bách hóa, Dược phẩm
status: watching | active | archived
last_updated: YYYY-MM-DD
source_files:
  - "nguồn (ngày)"
tags: [TICKER, sector, anti-thesis]
related:
  - "BCTC - Rolling.md"
  - "Thesis.md"
review_log:
  - YYYY-MM-DD: Hành động — mô tả
```

## 4. Catalyst-watch.md

```yaml
domain: investing
type: catalyst-watch
ticker: MWG
company_name: "Cổ phần Đầu tư Thế Giới Di Động"
sector: Bán lẻ
industry: ICT & Điện máy, Bách hóa, Dược phẩm
status: watching | active | archived
last_updated: YYYY-MM-DD
source_files:
  - "nguồn (ngày)"
tags: [TICKER, catalyst, ...]
related:
  - "BCTC - Rolling.md"
  - "Thesis.md"
review_log:
  - YYYY-MM-DD: Hành động — mô tả
```

## 5. Candidates_Watchlist.md

```yaml
domain: trading
tags: ["trading"]
type: tracking
status: active
last_updated: YYYY-MM-DD
tickers: [TICKER1, TICKER2, ...]
related: [030-Companies/{NUMBER}-{TICKER}/Thesis.md, ...]
```

## Rules (anti-patterns cần tránh)

| Anti-pattern | Why | Fix |
|---|---|---|
| `\|field: value` | Pipe ở đầu dòng vỡ YAML parser | Bỏ pipe |
| `data_status: active` | Chỉ `data_status: stub` được định nghĩa trong schema | Xóa field hoặc dùng `stub` nếu file chưa có dữ liệu |
| `last_updated: DD/MM/YYYY` | Sai format, phải YYYY-MM-DD | Sửa |
| `related` path không đồng nhất | Gây lỗi Obsidian graph view, Hermes search | Dùng format `030-Companies/{NUMBER}-{TICKER}/{File}.md` |
| `source_files` là string thay vì array | Schema yêu cầu array | Dùng `- "item"` |