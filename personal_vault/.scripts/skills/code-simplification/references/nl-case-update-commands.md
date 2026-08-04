# Natural Language Case Update Commands

## Overview
Extended the NL parser to support three new prefixes for case lifecycle management:
- `[update case] ...` - Append thread entry (newest on top)
- `[edit case] ...` - In-place frontmatter/body edit
- `[close case] ...` - Close with auto lesson learned vs success criteria

## Prefix Syntax

| Prefix | Behavior | Storage Pattern |
|--------|----------|-----------------|
| `[new case] desc` | Create new case file | New file in `_cases/active/` |
| `[update case <fuzzy>] text` | Prepend dated thread entry | `### YYYY-MM-DD HH:MM — Warren\ntext` |
| `[edit case <fuzzy>] instruction` | In-place frontmatter/body edit | Modifies existing file |
| `[close case <fuzzy>]` | Close + lesson learned | Move to `_cases/closed/`, add Close Review |

## Prefix Detection

```python
def detect_prefix(text: str) -> tuple[str, str, str]:
    """Returns (prefix, query, payload)"""
    # [new case] - no query, all payload
    # [update case query] payload
    # [edit case query] payload
    # [close case query] - no payload needed
```

## Implementation Details

### Update Case (Thread Append)
```python
def update_case_by_nl(path: Path, payload: str) -> str:
    data, body = parse_frontmatter(path)
    data["updated"] = today_str()
    
    # Prepend dated entry (NEWEST ON TOP)
    entry = f"### {datetime.now():%Y-%m-%d %H:%M} — Warren\n{payload}\n"
    updated_body = entry + "\n" + body
    
    # Update frontmatter
    data.setdefault("title", payload.splitlines()[0][:80])
    content = f"{format_frontmatter(data)}\n\n# {data.get('title')}\n{updated_body}"
    path.write_text(content, encoding="utf-8")
```

### Edit Case (In-Place)
```python
def edit_case_by_nl(path: Path, payload: str) -> str:
    data, body = parse_frontmatter(path)
    data["updated"] = today_str()
    
    # Frontmatter field edit
    field = detect_field(payload)
    if field:
        data[field] = payload.strip()
    
    # Body section edit
    section = detect_section(payload)
    if section:
        body = re.sub(
            rf"(## {re.escape(section)}\n)(.|\n)*?(?=\n## |\Z)",
            rf"\1{payload.strip()}\n",
            body
        )
    
    # Add edit marker
    updated_body = inject_update_entry(body, build_update_entry(f"Edited: {payload}"))
```

### Close Case (With Review)
```python
def close_case_with_review(path: Path) -> str:
    data, body = parse_frontmatter(path)
    
    # Extract success criteria from ## Thành công section
    success_section_match = re.search(r"## Thành công\n(.+?)(?:\n## |\Z)", body, re.S)
    success_text = success_section_match.group(1).strip() if success_section_match else "(no success criteria)"
    
    # Build close review
    review = f"""## Close Review
- Closed: {today_str()}
- Lesson learned: (auto)
- Insight: (auto)
- Success target: {success_text.splitlines()[0] if success_text else ''}
"""
    updated_body = inject_update_entry(body, review)
    
    data["status"] = "closed"
    data["updated"] = today_str()
    data["followup_event_id"] = ""
    
    # Move file to closed/
    shutil.move(str(path), str(CLOSED_DIR / path.name))
```

## Fuzzy Matching

```python
def find_case_by_query(query: str) -> Path | None:
    """Token overlap matching on slug + title"""
    query_tokens = tokenize(query)  # lowercase, remove punctuation
    for path in find_case_files():
        _, body = parse_frontmatter(path)
        slug_score = overlap_score(query_tokens, remove_prefix(path.stem))
        title_score = overlap_score(query_tokens, extract_title(body))
        score = max(slug_score, title_score)
        if score >= 0.35:  # Threshold
            return path
    return None
```

## Telegram Integration

```python
async def handle_text(message: types.Message):
    result = handle_message(message.text)
    # Chunk long responses (>4096 chars)
    for chunk in [result[i:i+4000] for i in range(0, len(result), 4000)]:
        await message.answer(chunk, parse_mode=ParseMode.HTML)
```

## Slug Format
```
YYYY-MM-DD_kebab-case-title
Example: 2026-06-19_testing-dao-vai-canned-moi
```

## Frontmatter Schema
```yaml
---
status: active|closed
store: lu3|lu5|lu7|lu3+lu5
opened: YYYY-MM-DD
updated: YYYY-MM-DD
priority: high|medium|low
follow_up: YYYY-MM-DD
followup_event_id: ""
stakeholders: "Warren, ops team"
owner: warren
title: "Case Title"
tags: "ops,revenue"
slug: "2026-06-19_test-case"
---
```

## Thread Format (Update Case)
```markdown
### 2026-06-19 14:30 — Warren
Payload text here...

### 2026-06-18 10:15 — Warren
Previous update...

## Vấn đề
Original issue...
```

## Close Review Format
```markdown
## Close Review
- Closed: 2026-06-19
- Lesson learned: (auto)
- Insight: (auto)
- Success target: [First bullet from ## Thành công]
```