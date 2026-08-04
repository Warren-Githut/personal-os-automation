# Template Skeleton vs Auto-Fill

## Misconception
"Template auto-fills itself" — **FALSE**. Templates are **skeletons**, not auto-filled forms.

## Reality

| Template Role | What It Does |
|---------------|--------------|
| **Skeleton** | Provides structure (4 sections: Vấn đề, Bối cảnh, Giải pháp đề xuất, Thành công) |
| **Placeholders** | `[Brackets]` show where to write, not auto-filled |
| **Defaults** | Frontmatter defaults (store=lu3, priority=high, etc.) |

## How Content Gets Filled

| Method | Who Fills | How |
|--------|-----------|-----|
| **NL Command** | Hermes (NL parser) | Parses free text → maps to 4 sections |
| **CLI Structured** | Warren (explicit args) | `--title`, `--store`, etc. |
| **Manual Edit** | Warren (Obsidian) | Opens file, types in sections |

## Template Example (Skeleton Only)
```markdown
---
status: active
store: lu3
priority: high
---
# {{title}}

## Vấn đề
[Mô tả vấn đề cụ thể]

## Bối cảnh
[Thông tin nền, dữ liệu liên quan]

## Giải pháp đề xuất
[Các option + tradeoffs + recommended reply]

## Thành công
- [Bullet 1]
- [Bullet 2]
- [Bullet 3]
```

## Key Principle
> **Template = Structure only. Content = User/Hermes input at runtime.**

The `[brackets]` are documentation, not template variables. They're replaced at creation time by:
- NL parser's section extraction
- CLI explicit arguments
- Manual typing in Obsidian

## Testing Template Usage
```bash
# NL — Hermes parses and fills
[new case] LU7 Matcha launch - cần sourcing matcha

# CLI — Explicit args fill frontmatter, body from template skeleton
ops-cases new --slug 2026-06-19_xyz --title "Title" --store lu7
```