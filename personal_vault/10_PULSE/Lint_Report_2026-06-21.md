---
domain: meta
type: tracking
status: active
last_updated: 2026-06-21
related: ["30_KNOWLEDGE_BASE/wiki/log.md"]
---

# Báo cáo lint Personal_OS — 2026-06-21

```text
Files checked : 131
Files clean   : 88
Files flagged : 43
Total issues  : 82
```

## Phân bổ lỗi

| Loại | Số | Ghi chú |
|---|---|---|
| Missing frontmatter | 17 | Không có khối `---` |
| Frontmatter thiếu field | 1 | File `_ideas/2026-05.md` |
| Status không hợp lệ | 9 | Chứa giá trị lạ như `unprocessed`, `watching`, `CODING`, `approved` |
| Broken wikilink | 55 | Link không trỏ tới file/wiki đích |

## Nhóm vấn đề theo vùng

### Vault chính
- `10_PULSE/GUIDE_agent_skills.md`: thiếu frontmatter
- `30_KNOWLEDGE_BASE/wiki/**`: nhiều broken link, phần lớn là link nội bộ và alias wiki chưa có đích

### _cases
- `_cases/README.md`: thiếu frontmatter

### _ideas
- `_ideas/2026-05.md`: thiếu field `created`, `title`

### _inbox / 02_processed_archived
- 8 file có `status: unprocessed` — không thuộc tập giá trị hợp lệ trong linter hiện tại

### .archive / .kilo arch / scripts
- Một loạt file không có frontmatter: đây là vùng thường không phải nội dung vault, nhưng nếu áp dụng chung rule thì vẫn bị phát hiện

### Wiki trading
- `030-Companies/031-GAS/Thesis.md`
- `030-Companies/033-NVL/Thesis.md`
- `030-Companies/034-PVD/Thesis.md`
- `030-Companies/035-HPG/Thesis.md`

→ 4 thesis dùng `status: watching` — cần chốt lại thuộc set hợp lệ hay mở rộng linter cho phép `watching`

## Khuyến nghị

1. **Tiêu chuẩn status chung:** định nghĩa rõ giá trị hợp lệ. Ví dụ mở rộng: `active, archived, draft, OPEN, CLOSED, stub, watching, deprecated, unprocessed, approved, CODING, PLANNING`.
2. **Quyết định frontmatter:** xác định các file “hỗ trợ” cần có frontmatter không (`README`, `_cases/README`, `Legacy reports`, `10_PULSE/GUIDE_agent_skills.md`).
3. **Broken wiki links:** loại trừ `obsidian-markdown` skill/doc trước; các broken link trong vault chính nên được audit từng nhóm (trading, family_gg).
4. **Repositories chéo:** `.archive/`, `.kilo/` nên thêm `scan-profile: false` hoặc trỏ linter chỉ vào vùng `active`.
