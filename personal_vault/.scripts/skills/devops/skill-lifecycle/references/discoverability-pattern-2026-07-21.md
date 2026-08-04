# Discoverability Pattern — Bài học 2026-07-21

## Bối cảnh

`gsheet-pivot-parser-pitfalls` là skill ops chất lượng, chứa 6 production failure modes từ hourly-cover parser W29 (thousands-separator crash → 37M net revenue vanished, subtotal misalignment → 10% drift, verify gate requirement...).

**Phát hiện:** Skill **chưa từng được load** (activity=0, curator report `never`). Lý do:
- Được tạo trong 1 session, save lại
- Không reference ở SOUL / session-start / bất kỳ index nào
- Không ai biết nó tồn tại

## Giải pháp (đã thực hiện)

1. **Pin skill** — `hermes curator pin gsheet-pivot-parser-pitfalls`
2. **SOUL §7 reference** — thêm 1 dòng bảng index + 1 paragraph trigger
3. **SOUL.md last_updated** → cập nhật ngày

## Cụ thể — SOUL.md edit

```markdown
| Parser Pitfalls | skill `gsheet-pivot-parser-pitfalls` — load khi debug GSheet parser pipeline |

> **Parser work:** Khi debug/sửa GSheet parser pipeline → load skill `gsheet-pivot-parser-pitfalls` (đã pin, curator không archive).
```

## Tác động

- Từ giờ, khi làm parser work, Hermes sẽ thấy dòng này và load skill
- Curator không archive dù 90d unused
- Cross-link: `gsheet-pivot-parser-pitfalls.related_skills` nên trỏ `skill-lifecycle`

## Câu hỏi của Warren

> "Useful sao không xài?"

Đây là vấn đề **discoverability gap** — knowledge management kinh điển:
- Knowledge tồn tại (skill có content)
- Knowledge không được index/reference (không ai biết để dùng)
- Knowledge decay (skill bị archive sau 90d)

Ẩn ý: Bố muốn mọi thứ tạo ra phải có ích thực tế, không lãng phí.
