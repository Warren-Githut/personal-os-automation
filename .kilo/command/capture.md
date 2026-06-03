---

description: "Knowledge capture from web/YouTube/social — ORION creates atomic .md file in _growth/ + updates _INDEX.md"
updated: 2026-06-02
---

# /capture — Knowledge Capture

# v1.0 | 2026-05-29 | Phase 2
# PURPOSE: Warren pastes link/text → ORION parses → creates atomic .md file in _growth/ → updates _INDEX.md
# Non-IT friendly: ORION asks clarifying questions, suggests tags, auto-detects source type.

---

## Usage

```
/capture [URL or text] [optional: --vault lu|personal] [optional: --tags tag1,tag2]
```

Example:
```
/capture https://youtube.com/watch?v=xxx
/capture "Book Radical Candor has this good idea..." --tags leadership,communication
/capture https://x.com/user/status/xxx --vault personal --tags trading,psychology
```

---

## Protocol — 5 Steps

### STEP 1 — PARSE & AUTO-DETECT

ORION parses input, auto-detects:

| Input has | Auto-detect | Confidence |
|----------|------------|------------|
| URL youtube.com / youtu.be | `source_type: youtube` | HIGH |
| URL x.com / twitter.com / linkedin.com | `source_type: social` | HIGH |
| URL amazon.com / goodreads.com | `source_type: book` | HIGH |
| URL with /article/ /blog/ /post/ | `source_type: article` | MOD |
| Text without URL + mentions "book" | `source_type: book` | MOD |
| URL podcast / spotify | `source_type: podcast` | HIGH |
| Cannot detect | `source_type: other` | LOW |

If URL present → ORION fetches to get title/description (use `webfetch`).

### STEP 2 — VAULT ROUTING

Determine target vault:

| Condition | Vault |
|-----------|-------|
| Tags include `#lu`, `#lu3`, `#lu5`, `#lu7`, `#ops`, `#leadership`, `#cx`, `#cogs`, `#labour` | `lu` (Warren_OS_Local) |
| Tags include `#trading`, `#health`, `#parenting`, `#gg`, `#personal`, `#finance`, `#btc` | `personal` (Personal_OS) |
| Warren specifies `--vault lu` or `--vault personal` | As specified |
| **Unclear** → ask Warren 1 question | Wait for confirmation |

### STEP 3 — SUGGEST & CONFIRM (non-friction)

ORION suggests then asks Warren to confirm **exactly once**:

```
→ Capture to: [vault]/_growth/
→ Title: "[suggested title]"
→ Domain: [suggested domain]
→ Tags: [suggested tags]
→ Source: [source_type] — [source_name]

OK? (type "ok" or edit: "domain: leadership, tags: comm, feedback")
```

**Rule:**
- If Warren already provided sufficient `--vault`, `--tags` → skip confirm, create immediately
- If missing info → suggest + confirm once
- Warren can edit any field in the confirm

### STEP 4 — CREATE FILE

ORION creates `.md` file in the correct directory:

| Vault | Path |
|-------|------|
| `lu` | `C:\Users\khoans\Documents\Warren_OS_Local\vault\_growth\` |
| `personal` | `C:\Users\khoans\Documents\Personal_OS\personal_vault\_growth\` |

**File name:** `YYYY-MM-DD_[slugified-title].md`
- `slugified-title`: lowercase, no diacritics, replace spaces with `-`, max 80 characters
- Example: `2026-05-29_cach-noi-chuyen-voi-nhan-vien-khi-vi-pham-ky-luat.md`

**Template file (ORION must follow EXACTLY):**

```yaml
---
domain: [domain]           # required
tags: ["tag1", "tag2"]     # 1-5 tags, required
source_type: [youtube/book/social/article/podcast/other]  # required
source_name: "[channel/author/book name]"    # required if available
source_url: https://...     # optional
date_captured: YYYY-MM-DD   # required
last_reviewed: YYYY-MM-DD   # required
status: active              # required
---

# [Short title — 1 sentence]

## Source
[Channel / book / article / author name]
[URL if available]

## Key Takeaways
- [Key point 1]
- [Key point 2]
- [Key point 3]

## [Application for L'Usine / Application]
- [Where can this be applied — 1-2 sentences]

## Notes
[Additional content if needed]
```

> **Note:** The "Application" section changes by vault:
> - LU vault → `## Application for L'Usine`
> - Personal vault → `## Application`


### STEP 4.5 — CROSS-LINK DETECTION (if Warren mentions continuation)

**Trigger phrases** — ORION auto-detects when Warren says:
- "part 2", "phần 2", "p2", "next", "nối tiếp", "continuation"
- "related to file...", "similar to file...", "same topic as..."
- "link with...", "supplement to..."

**Do not trigger** if Warren doesn't mention continuation.

---

#### 4.5A — Find related files

ORION scans `_INDEX.md` in target vault, finds matching files by:

| Search method | Priority |
|----------|---------|
| Warren specifies exact filename or keyword | 1 — use directly |
| Same `domain` + at least 2 matching `tags` | 2 — suggest |
| Same `domain` + matching keywords in title | 3 — suggest |
| No match found | Ask Warren: "No related files found. Do you remember the filename?" |

#### 4.5B — Confirm with Warren

ORION lists 1-3 best matching files, asks 1 question:

```
Found related files:
  [1] 2026-05-29_cach-noi-chuyen-voi-nhan-vien-khi-vi-pham-ky-luat.md (leadership)
  [2] 2026-05-15_radical-candor-framework.md (leadership)

Link with which file? (number, "all", or "none")
```

Warren selects → ORION proceeds.

#### 4.5C — Create cross-link

After creating new file, ORION appends to **last line** of **both files**:

**New file (Part 2):**
```
---
... (YAML frontmatter) ...
---

# [Title]

... (main content) ...

---

> 📎 Related: [[2026-05-29_cach-noi-chuyen-voi-nhan-vien-khi-vi-pham-ky-luat|Part 1 — How to talk to employees when they violate discipline]]
```

**Old file (Part 1) — ORION appends to end:**
```
---

> 📎 See also: [[2026-05-30_cach-noi-chuyen-voi-nhan-vien-p2|Part 2 — (part 2 title)]]
```

**Link format:**
- LU vault: `[[filename|Part N — title]]`
- Personal vault: same
- Always use `---` (horizontal rule) to separate from main content
- Always append at **end of file**, do not insert in the middle of content

#### 4.5D — Multiple related files

If Warren chooses "all" → ORION links new file with **all** selected files:
- New file has multiple `📎 Related: [[...]]` lines
- Each old file has 1 `📎 See also: [[new file]]` line

---

### STEP 5 — UPDATE INDEX

ORION updates `_INDEX.md` in the same directory:

1. **Add 1 new row** to File Index table — **at top** (newest on top)
2. Update **Stats** (total files + last updated)
3. New row format:

```
| YYYY-MM-DD | [filename.md](filename.md) | domain | tags | Source | 1-line description | YYYY-MM-DD |
```

**Example new row:**
```
| 2026-05-29 | [2026-05-29_cach-noi-chuyen-voi-nhan-vien.md](2026-05-29_cach-noi-chuyen-voi-nhan-vien.md) | leadership | communication, feedback | YouTube — Simon Sinek | How to talk to employees when they violate discipline | 2026-05-29 |
```

### OUTPUT

After completion, ORION reports:

```
✅ Capture complete → `_growth/2026-05-29_cach-noi-chuyen-voi-nhan-vien.md`
Tags: leadership, communication | Vault: L'Usine
```

---

## Error Handling

| Situation | ORION handles |
|-----------|------------|
| URL fetch fail (timeout, block) | Write `source_name: "[Could not fetch — Warren fills in]"` |
| File already exists (duplicate name) | Add suffix `-2`, `-3` to filename |
| `_INDEX.md` not found | Report error, create new file, ask Warren |
| Warren pastes text too short (<10 characters) | Ask: "What is the key takeaway of this knowledge?" |

---

## Anti-patterns

- ❌ Create file without YAML frontmatter
- ❌ Forget to update `_INDEX.md`
- ❌ Choose vault arbitrarily when unclear — must ask Warren
- ❌ Create file in `wiki/` instead of `_growth/`
- ❌ Use template different from template in `_INDEX.md`

---

**v1.0 | 2026-05-29 | Phase 2 — Knowledge Capture Pipeline**
