# Wiki File Maintenance — Rename / Merge / Rolling

> Patterns từ cleanup `04_labour_costs/` (2026-07-01).
> Dùng khi cần restructure wiki files: rename, merge, hoặc convert sang rolling format.

---

## 1. Rename File in Wiki Folder

**When:** File name không chính xác (vd `02_HR_Movements` trong folder `04_` + các file khác ko có prefix).

**Steps:**

1. `mv` file → new name (trong cùng folder)
2. Update frontmatter: `name:` field
3. Update title: `# ...`
4. Update WIKI INDEX entry (file path + key_insights nếu cần)
5. Update cross-references — grep vault-wide cho old filename:
   ```bash
   search_files path=vault pattern=<old-filename> target=content file_glob=*.md
   ```
   Fix mọi `[[wikilinks]]` và `related:` references.
6. Verify: `ls` file tồn tại, INDEX entry đúng, grep old filename = 0

**Pitfalls:**

| Pitfall | Fix |
|---------|-----|
| `patch` tool fails (non-unique pattern) | Dùng `sed -i` thay thế: `sed -i 's/old-name/new-name/g' file.md` |
| Lỡ tay dùng `||` thay vì `|` trong INDEX table | Dùng `sed -n 'Np' file \| cat -A` để check raw pipe characters |
| INDEX entry bị mất sau nhiều edits | Re-read file đầy đủ trước mỗi patch. Verify cuối: count rows match expected. |
| Total_files count sai | Count bằng `ls | grep -c "^-"` trong folder, update frontmatter. |

---

## 2. Merge Multiple Files → One

**When:** 2+ files chồng chéo content, có thể gộp.

**Steps:**

1. **Identify unique content** — đọc full từng file, liệt kê sections không overlap
2. **Determine target** — file nào là SSOT (thường là data log ở `10_OPERATION_DATA/` hoặc wiki analysis)
3. **Create merged content** — structure rõ: mỗi source file = 1 section trong target. Giữ template của target.
4. **Delete source files** — `rm` từng file cũ
5. **Update WIKI INDEX** — remove source entries, add target if new. Bump `total_files` (net change = -N+1 nếu target mới, -N nếu target cũ).
6. **Update cross-refs** — grep cho old filenames vault-wide, patch to merged file name

**Pitfalls:**

| Pitfall | Fix |
|---------|-----|
| Content không tương thích (data file vs analysis file) | Tách section rõ: data section + analysis section. Không trộn lẫn. |
| Template format khác nhau | Giữ template của target file. Chuyển content từ source sang format của target. |
| Cross-refs trong source file `related:` field | Chuyển `related:` từ source vào target. |

---

## 3. Convert Year-Specific → Rolling Format

**When:** File có year trong tên (`Extra_Hours_Tracking_2026.md`) nhưng sẽ dùng nhiều năm.

**Steps:**

1. `mv` file → bỏ year, thêm `_Rolling`
2. Update frontmatter: `name:` bỏ year
3. Update title: `# ... 2026` → `# ... Rolling`
4. Add perpetual instruction ngay sau title:
   ```markdown
   > **Perpetual rolling file.** Mỗi year = new section. [Year] data below.
   > Khi [next year] starts, add `## [Year]` section above — no rename needed.
   ```
5. Update WIKI INDEX: rename entry, update `type:` nếu cần (có thể thành `rolling`)
6. Update cross-refs — grep cho old filename

---

## 4. Create Rolling Log from One-Off Report

**When:** Report chỉ cho 1 period (vd `CEO_COL_Crisis_Report_W26.md`) nhưng sẽ làm định kỳ.

**Steps:**

1. Tạo **template file** riêng (framework/TL;DR form — reusable sections với placeholder)
2. `mv` report file → tên rolling log
3. Update frontmatter: thêm `template:` field trỏ đến template file. Change `type:` từ `report` → `rolling`
4. Prepend rolling header:
   ```markdown
   > **Rolling log.** Append new report above existing. Template: `TemplateFile.md`.
   ```
5. Tag existing report là entry đầu tiên với period header:
   ```markdown
   ## 2026-W26 | date range — Title
   ```
6. WIKI INDEX: thêm 2 entries (template + rolling). Update total_files (+1 so với trước).
