# NL Command Pattern (Telegram/Slack/Obsidian)

## Problem
Users want to create/update/close cases via natural language in Telegram/Slack/Obsidian without strict CLI syntax.

## Solution: Prefix-Based NL Parsing

### Supported Prefixes
| Prefix | Behavior | Example |
|--------|----------|---------|
| `[new case] <payload>` | Create new case | `[new case] LU7 Matcha launch` |
| `[update case <fuzzy>] <payload>` | Append thread entry (newest on top) | `[update case matcha] found supplier` |
| `[edit case <fuzzy>] <payload>` | In-place frontmatter/body edit | `[edit case matcha] priority high` |
| `[close case <fuzzy>]` | Close + lesson learned/insight | `[close case matcha]` |

### Fuzzy Matching
```python
def find_case_by_query(query: str) -> Path | None:
    tokens = tokenize(query)  # lowercase, remove diacritics, split
    for path in find_case_files():
        slug_score = overlap_score(tokens, remove_prefix(path.stem))
        title_score = overlap_score(tokens, extract_title(path))
        score = max(slug_score, title_score)
        if score > best_score and score >= 0.35:
            best = path
```

### Thread Format (Newest on Top)
```markdown
### 2026-06-19 14:30 — Warren
đã tìm được NCC mới, giảm 30% chi phí

### 2026-06-18 10:15 — Warren
đã đàm phán ban đầu

## Vấn đề
Container cost tăng 20%...
```

### Close Review (Auto-Generated)
```markdown
## Close Review
- Closed: 2026-06-19
- Lesson learned: (auto)
- Insight: (auto)
- Success target: Giảm chi phí 30%
```

## CLI Equivalents
| NL Prefix | CLI Command |
|-----------|-------------|
| `[new case] ...` | `ops-cases new --slug ... --title ...` |
| `[update case x] y` | `ops-cases update "x" "y"` |
| `[edit case x] y` | `ops-cases edit "x" "y"` |
| `[close case x]` | `ops-cases close-nl "x"` |

## Integration Points
| Channel | How |
|---------|-----|
| Telegram Bot | Webhook → `handle_message("[update case ...]")` |
| Slack #brain-dump | Same parser, different webhook |
| Obsidian | Direct file write with prefix |
| CLI | `ops-cases update "fuzzy" "payload"` |