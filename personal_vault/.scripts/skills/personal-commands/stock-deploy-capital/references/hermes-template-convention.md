# HERMES TEMPLATE — Growing File Convention (v1.1)

## Pattern

Mọi file **growing** (prepend newest on top) trong vault phải có `<!-- HERMES TEMPLATE -- ... -->` ngay dưới YAML frontmatter, trên entry mới nhất.

Template guide = HTML comment block (`<!-- ... -->`). Hiển thị trong Obsidian edit mode, ẩn khi render.

## Cấu trúc file

```yaml
---
# YAML frontmatter (rich metadata — càng nhiều càng tốt để Hermes extract/retrieve)
domain: trading | health | finance | ...
type: tracking | log | report
status: active
created: YYYY-MM-DD
last_updated: YYYY-MM-DD
entries: <số entry>
tickers: [TICKER1, TICKER2]        # chỉ cho stock files
verdicts:
  TICKER1: "🔫 BẮN" | "⏳ CHỜ" | "🛑 TRÁNH"
scores:
  TICKER1: <điểm>
valuation_status:
  TICKER1: "✅ PASS" | "🛑 FAIL"
preflight:
  fomo: "Conviction" | "FOMO"
  vnindex_200dma: true | false
  enough_cash: true | false
market:
  brent_oil: <giá>
  vnindex_level: <giá>
  interest_rate_environment: neutral | tight | loose
source_files_scanned:
  - path/to/file1.md
  - path/to/file2.md
live_price_source: <nguồn>
related:
  - File1.md
  - File2.md
---
```

## Template comment format

```html
<!--
HERMES TEMPLATE — [Title] (vX.X)

Mỗi entry có N sections theo thứ tự:

1. ### Section 1 — mô tả
2. ### Section 2 — mô tả
3. ...
-->
```

## Rules

1. **Template ở dòng đầu tiên sau frontmatter** — không blank line giữa `---` và `<!--`
2. **Dòng đầu template:** `HERMES TEMPLATE — [Title] (vX.X)`
3. **Liệt kê sections theo thứ tự** — mỗi entry PHẢI theo đúng thứ tự này
4. **Kết thúc bằng** `-->`, sau đó blank line rồi entry mới nhất
5. **Entry order:** newest on TOP (prepend), oldest at bottom
6. **Entry format:** markdown, theo đúng sections trong template
7. **Không chỉnh sửa template guide** khi update entry — chỉ đọc để biết cấu trúc

## Yêu cầu frontmatter khi prepend entry mới

Khi thêm entry mới, **PHẢI update các field sau** trong frontmatter:

| Field | Action |
|-------|--------|
| `last_updated` | Cập nhật ngày hiện tại |
| `entries` | Tăng lên 1 |
| `tickers` | Merge nếu có ticker mới |
| `verdicts` / `scores` / `valuation_status` | Thêm/update per ticker |
| `preflight` | Ghi lại answers mới |
| `market` | Cập nhật nếu có số liệu mới |
| `source_files_scanned` | Merge nếu scan thêm file |

## Example (thực tế từ vault)

File: `VN_Equities/040_Deploy_Capital_Report.md` (xem file để thấy template + entry đầu tiên cho GAS 83/100)

## Tại sao cần

Hermes context không lưu cấu trúc file giữa các session. Template guide ở đầu file = Hermes đọc được ngay cấu trúc trước khi write/edit, không cần đoán hay nhớ từ session trước. Rich frontmatter = Hermes extract data bằng YAML parser, không cần grep nội dung.
