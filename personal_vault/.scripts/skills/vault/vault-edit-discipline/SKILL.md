---
name: vault-edit-discipline
description: "Vault .md editing discipline — khi đổi 1 giá trị/giá/quyết định đã nằm rải rác trong file, phải grep toàn bộ occurrence trước + sau, patch TẤT CẢ, verify 0 leftover. Áp dụng mọi edit vault file (case, wiki, index, memory)."
version: 1.0.0
trigger:
  - "Warren yêu cầu đổi 1 giá trị đã xuất hiện nhiều lần trong file (giá, tên, status, tag)"
  - "Edit vault .md có >1 chỗ cùng 1 thông tin cần thay đổi"
  - "align lại, check toàn bộ, đổi X thành Y ở mọi chỗ"
tags: ['vault', 'edit', 'align', 'grep', 'discipline']
---

# Vault Edit Discipline — Align-All Rule

> **Class-level rule cho mọi edit vault file.** Không riêng case-lifecycle.

## THE CORE PITFALL (Incident 2026-07-16)

Khi đổi 1 giá trị đã nằm rải rác (vd: combo 169k → tách sáng 169k / tối 189k), Hermes patch theo trí nhớ → **SÓT 1-2 chỗ** (standee tối vẫn ghi "169k + kem bé free", POS note, exec summary). Warren bắt align lại. Lỗi do không grep-all trước/sau.

## THE RULE (bắt buộc)

Mỗi lần đổi 1 giá trị xuất hiện >1 lần trong file:

1. **GREP-ALL TRƯỚC:** terminal chạy `grep -n "giá_trị_cũ" <file>` → liệt kê MỌI dòng có occurrence.
2. **PATCH TẤT CẢ:** dùng patch từng chỗ (hoặc write_file merged nếu delimiter lặp). KHÔNG được sót.
3. **GREP-ALL SAU:** `grep -n "giá_trị_cũ"` lại → confirm **0 leftover** (trừ khi cố ý giữ ở 1 chỗ có context rõ).
4. **Nếu đổi ảnh hưởng xuyên file (vd: giá combo ở case + measurement sheet + index):** lặp lại bước 1-3 cho TỪNG file liên quan.

## TOOLING NOTE (Windows/git-bash)

- `search_files` tool **FAIL** trên git-bash path (`/c/Users/...` → IO error os 3, hoặc trả **rỗng `total_count:0` dù file tồn tại**). ❌ Sai: "không tìm thấy = không tồn tại". ✅ Đúng: rỗng ≠ không có → luôn verify bằng `terminal`.
- **Khi search_files trả rỗng/IO error:** chạy `terminal` để locate thực tế:
  - `find /c/Users/khoans -iname "SOUL.md" 2>/dev/null` (tìm file theo tên)
  - `ls -la /c/Users/khoans/Documents/Stock_OS/stock_vault/00_CORE_LOGIC/` (list folder)
  - `grep -rn "personal_vault" "/c/Users/khoans/Documents/Stock_OS/stock_vault/00_CORE_LOGIC/"` (grep xuyên file)
  - Session 2026-07-18: search_files báo 0 kết quả cho SOUL.md/STOCK_MEMORY.md → con tưởng vault mất. Thực tế `find` tìm thấy ở `Stock_OS/stock_vault` (không phải `Personal_OS/personal_vault` như memory ghi). Lỗi này từng làm con định đọc nhầm file / báo sai path.
- `patch` tool báo "Found N matches" khi old_string trùng → dùng `terminal` python với `assert s.count(marker)==1` để insert an toàn, hoặc `write_file` merged content.
- **Git trong MSYS bash:** `git add "<path>"` trong chain `&&` (vd `cd repo && git add "vault/..." && git commit && git push`) thường báo `pathspec '...' did not match` do quote bị shell parse sai. **Fix:** tách `cd <repo> && git add <relpath>` thành command RIÊNG (không chain), rồi `git commit` / `git push` cũng riêng lệnh. `git -C <abs_repo> add <relpath>` đôi khi cũng fail → thà tách command. Luôn verify `git status --short` thấy ` M` (unstaged) hoặc `M ` (staged) trước commit. (Session 2026-07-26: mất 3 lần thử do chain `&&` → tách riêng mới add được.)

## INSERT CLICKABLE DASHBOARD LINK — PATTERN (2026-07-20)

Warren hay yêu cầu "cho bố 1 clickable link ở top file .md, link tới dashboard .html". Quy trình chuẩn:

1. **VERIFY TARGET HTML TỒN TẠI** bằng `terminal ls` (KHÔNG dùng search_files — false-negative IO error trên Windows, đã gặp session này). Link `file:///` tới file không tồn tại = dead link trong Obsidian.
2. **VỊ TRÍ CHÈN:** ngay SAU frontmatter `---` đóng, TRƯỚC bất kỳ `<!--` comment opener hoặc `# Title`. Format:
   ```
   > 📊 **[<Tên Dashboard>](file:///C:/Users/khoans/Documents/Warren_OS_Local/vault/<path>/<file>.html)** — xem chart xu hướng
   ```
   Dùng `file:///` (mở bằng browser mặc định). Nếu muốn mở trong Obsidian tab → dùng `[[<relpath>]]` (nhưng HTML thường mở ngoài tốt hơn).
3. **⚠️ PITFALL — LINK BỊ ẨN TRONG COMMENT:** nhiều tracker file có block `<!-- HERMES TEMPLATE ... -->` dài (vd COL: mở line 36, đóng line 730). Nếu file ĐÃ có dòng dashboard link NHƯNG nằm TRONG comment → Obsidian ẩn, Bố bấm không được. PHẢI chèn link MỚI ra NGOÀI comment (trước dấu `<!--`), giữ dòng cũ trong comment nguyên (part of template). Đừng patch đè vào trong comment.
4. **PATCH UNIQUE:** `---` frontmatter delimiter lặp nhiều lần trong file → `patch` fuzzy báo "Found N matches" (session này: 7–22 matches). Fix: đưa đủ context — kèm template header + heading section đầu (vd `## 2026-W29 | ...` hoặc `# Wastage Write-Off Monthly Log` + dòng `<!--` + box-drawing đầu). KHÔNG chỉ dùng riêng dòng `---`.

## VERIFY SCRIPT (zero-discretion table check)
- **`scripts/verify_obsidian_tables.py <file.md>`** — deterministic check that ALL tables render in Obsidian. Catches the 3 break modes (blank-between-rows, emoji-in-cell, mojibake), counts REAL (non-comment) regions, exits 1 if any broken. Run AFTER any edit touching vault tables; do NOT claim "done" until it prints `CLEAN`.
- **Reusable fix pipeline** (from 2026-07-20 COGS fix): (1) strip emoji in `|` cells -> R/Y/G, (2) `s.encode('cp1252').decode('utf-8')` to reverse mojibake, (3) delete every blank line + `>` blockquote sitting between two table rows. Then run the verifier.
- **`scripts/fix_obsidian_tables.py <file.md>`** — RUNNABLE version of the 3-step fix above (rewrites file in place; caller `cp` to `%LOCALAPPDATA%\Temp` first). Chains the verify logic and prints `CLEAN`/`BROKEN`. Use it instead of hand-typing the transform when a vault table renders as `|||`.

## PRE-EDIT CHECKLIST (rút gọn)

- [ ] Giá trị cũ xuất hiện bao nhiêu lần? (grep -n)
- [ ] Đã patch hết mọi chỗ?
- [ ] Grep lại = 0 leftover?
- [ ] File liên quan khác (index, sub-file, measurement) có cần đổi theo không?

## PITFALLS

| Pitfall | Fix |
|---------|-----|
| Patch sót 1 chỗ vì nhớ sai số occurrence | Grep -n trước/sau, không dùng trí nhớ |
| Đổi trong case nhưng quên measurement sheet / index | Đổi xong check mọi file cross-reference |
| search_files báo IO error HOẶC rỗng (total_count:0) trên git-bash | Dùng terminal `find`/`ls`/`grep -rn` để verify, tuyệt đối không kết luận "file không tồn tại" từ search_files |
| patch fail "Found N matches" (N≥2) | old_string chưa unique. 2 nguyên nhân + fix: (1) **Header lặp** — vd `### LU3/LU5/LU7 — Promos đang chạy` gần giống nhau → fuzzy match va N chỗ. Fix: KHÔNG dùng header làm anchor; thay vào đó anchor vào dòng DUY NHẤT ngay TRƯỚC target (vd `- **Cadence:** Điền kết luận...` — chạy `grep -n` confirm count==1), chèn block lên trước dòng đó. (2) Dòng `---` lặp → thêm context (template header + heading). Mọi trường hợp: `grep -n "anchor" <file>` để CHẮC CHẮN count==1 trước khi patch; nếu grep báo >1 → mở rộng context hoặc dùng terminal python `assert s.count(marker)==1` rồi `s.replace(marker, new)`. (Session 2026-07-26: case quick-wins có 3 header LU3/LU5/LU7 giống hệt → patch báo "Found 3 matches"; fix = anchor dòng Cadence duy nhất.) |
| YAML frontmatter list bắt đầu `date:` báo mapping error | Bọc giá trị trong ngoặc kép. YAML coi `date:` là KEY, không phải value. |
| THIẾU closing `---` sau frontmatter → body bị nuốt thành frontmatter → Obsidian lỗi + link mất | Luôn có CẶP `---`. Sau edit frontmatter verify bằng execute_code: regex match `^---\n(.*?)\n---\n` (DOTALL), assert không None (None = thiếu đóng), rồi yaml.safe_load(group1). (2026-07-20: 09_Hourly_Cover_Revenue_Log.md thiếu `---` đóng → link dashboard mất, fix = chèn `---` + promote link thành `[!tip]` callout.) |
| External descriptor (Google Calendar, cron prompt) DRIFT khỏi vault | Khi Warren hỏi có cần update không → cross-check vs DISK: dashboard path (verify tồn tại), parser version (frontmatter), week token (W28 cứng ≠ W29 hiện tại), tab/sheet name. Sản xuất bản ĐÃ SỬA sẵn (copy-paste), dùng `Wxx` template thay hardcode tuần. |
| Dashboard link chèn vào file .md NHƯNG nằm TRONG `<!-- ... -->` comment block → Bố không thấy/bấm được | Chèn link ra NGOÀI comment (trước `<!--` opener). Check boundary comment bằng `grep -n -- ">"` trước khi chèn. |
| `search_files` báo `total_count:0` / IO error khi tìm file .html target → kết luận "dashboard không tồn tại" rồi không chèn link | SAI. Verify bằng `terminal ls -la <path/to/file.html>` — session này dashboard THẬT tồn tại dù search_files báo 0. |
| `patch` báo "Found 7/22 matches" khi old_string chỉ là dòng `---` | `---` lặp nhiều lần. Thêm context (template header + heading + comment opener) để unique. |
| **Obsidian bảng vỡ (||| raw) do DÒNG TRỐNG giữa các row** | File COGS log từng có **309 dòng trống nằm XEN GIỮA 2 row bảng** → Obsidian cắt bảng, in raw `| |`. Emoji-in-cell (WARREN_MEMORY dòng 413) CHỈ là 1 trong 3 lớp. Khi fix bảng vỡ: (1) strip emoji ô → R/Y/G, (2) reverse mojibake, (3) **XÓA MỌI blank line + dòng `>` blockquote nằm giữa table rows**. Verify = scan TẤT CẢ table regions (không chỉ block đầu), đếm blank-in-table = 0. |
| **Bảng/list bị WRAP TOÀN BỘ trong `>` blockquote → Obsidian KHÔNG render (hiện `|||` raw)** | Khác với pitfall "blockquote GIỮA rows" (table vẫn top-level): nếu MỌI dòng của 1 bảng/list có prefix `> ` (vd copy "recommended text" từ handoff/chat dùng `>` để quote rồi paste nguyên vào vault) → Obsidian coi toàn bộ là blockquote, **KHÔNG parse thành table** → in raw `| |`. **Fix:** trước ghi vault, STRIP mọi `> ` đầu dòng của block được paste. Quy tắc: bảng markdown + bullet list PHẢI ở top-level (không nằm trong blockquote) mới render. `>` chỉ dùng cho callout 1 dòng (vd `> 📊 link`), KHÔNG wrap multi-line table/list. (Session 2026-07-26: block W29 measurement copy nguyên `>` từ handoff → Bố bắt lỗi `|||`; fix = bỏ `>` prefix, bảng render đúng.) **→ Copy-ready template chuẩn: `templates/measurement_block_vault.md` (bảng top-level + biến thể 🚩 FLAG pre-launch).** |
| **Claim "done" khi chưa verify TẤT CẢ block** | Session 2026-07-20: fix xong block 07 (tháng 7) rồi báo xong, NHƯNG block 06 + 05 ở CUỐI file (line >500) vẵn hỏng (mojibake + blank). Warren bắt: "vẫn hiện |||". LUẬT: khi sửa file có N block (tháng/quý), PHẢI đọc TOÀN BỘ file (read_file offset tới cuối) + verify từng block trước khi báo done. Đừng báo xong sau khi chỉ check 1 phần. |
| **Verify "table OK" phải đếm regions thực (ngoài comment)** | HTML `<!-- ... -->` template comment chứa bảng mẫu → Obsidian ẨN toàn bộ, KHÔNG vỡ. Khi verify "0 broken table": chỉ tính bảng NGOÀI comment (skip `<!-`-`-->`). Đừng để bảng trong comment thành false-positive "broken" cũng đừng bỏ sót bảng thật. Script: parse `is_table_line` + track `in_comment` flag. |
| `patch` KHÔNG match được `|||` (triple pipe) trong Obsidian double-pipe table | Session 2026-07-21: file USER.md dùng format `||` (Obsidian double-pipe table). Sau 1 lần patch sai tạo `|||` (triple pipe) ở 3 dòng. Gọi `patch` với old_string chứa `|||` → tool báo "success" NHƯNG thực tế không đổi gì (read_file vẫn thấy `|||`). `replace_all=true` → báo "Could not find a match". `sed -i 's/^||| /|| /g'` cũng không ăn. **Fix:** đọc toàn bộ file (`read_file` full) → sửa lỗi trong Python string → `write_file` overwrite. KHÔNG dùng `patch` cho Obsidian table rows. |
| **YAML frontmatter `review_log:` list item `YYYY-MM-DD: text` báo ScannerError** (2026-07-23, Stock_OS Candidates_Watchlist.md) | Variant của pitfall `date:` cột 11. Item `- 2026-07-20: Thêm BSR — ...` → PyYAML `ScannerError: mapping values are not allowed here` vì coi `2026-07-20:` là KEY. **Fix:** bọc nguyên item trong ngoặc kép: `- "2026-07-20: Thêm BSR — ..."`. Regex one-liner: `s = re.sub(r'^(\s*- )(\d{4}-\d{2}-\d{2}: .*)$', lambda m: m.group(1)+'"'+m.group(2)+'"', s, flags=re.M)`. Validate bằng `yaml.safe_load(fm)` sau edit. |
| **Markdown bảng lệch cột do ô ĐẦU (Mã/ticker) để trống** (2026-07-23, Watchlist) | Nếu cell đầu tiên của 1 row trống, toàn bộ row trượt phải 1 cột (tên đẩy sang cột Ngành, mọi cột lệch). Symptom: BSR/GAS/PNJ rows có blank Mã. **Fix:** luôn điền ticker vào cell ĐẦU. Plus XÓA các dòng bảng hoàn toàn rỗng (chỉ có `| | | | ... |`) — chúng render thành garbage row và làm sai column count. Verify: đếm số cell mỗi row == header cell count. |
| **APPEND block vào log "newest-on-top" = dùng `patch` replace TỪ BLOCK GIỮA file** (2026-07-26, LTO log) | File có W28(top)→W27(bottom). Con `patch` old=`## W28...` new=`W28_new + W27_new + W29` → KẾT QUẢ: giữ nguyên thứ tự cũ (W28 trên, W27 dưới) + chèn W29 xuống ĐÁY (sai, W29 phải TRÊN CÙNG). Lý do: `patch` replace từ giữa KHÔNG thay đổi vị trí tương đối của các block còn lại → block mới lọt xuống đáy. **Fix (newest-on-top):** INSERT block mới NGAY SAU dòng `---` đóng frontmatter (trước heading `## ` đầu tiên), KHÔNG replace từ giữa. Cách: (a) `write_file` rewrite toàn bộ body với block mới ở đầu, HOẶC (b) `patch` old_string = `---` đóng + `## heading_đầu_tiên` → new_string = `---` + block_mới + `## heading_đầu_tiên`. SAU patch → `read_file` line 44-45 verify block mới nằm ngay sau frontmatter (KHÔNG ở cuối). |
| **AUTO-GENERATED vault file — hand-edit bị cron ghi đè** (2026-07-27, TODAY.md) | File có dòng `Generated by Hermes` / sinh bởi cron (vd `TODAY.md` ← `gen_today.py`, cron 09:00, `TODAY_FILE.write_text(content)` ghi đè TOÀN BỘ). Con sửa tay 1 section (vd COL 26/07) → lần cron sau WIPES sạch → Warren: "vì sao con ko update file này?". | **KHÔNG hand-edit file auto-gen.** Tìm generator trước: `grep -rn "write_text" vault/.scripts/ | grep <filename>` hoặc `grep -rn "TODAY.md" vault/.scripts/`. Patch GENERATOR để sinh section đó (vd thêm `_build_col_latest_section()` đọc latest row từ GSheet `07_COL_Weekly_Log`). Nếu cần sửa tay 1 lần: ghi chú "ephemeral, sẽ bị ghi đè" + warn Bố. **Quy tắc:** trước edit bất kỳ .md nào có `Generated by Hermes` hoặc comment `Output: overwrites ...<file>` → tìm generator, sửa generator chứ không sửa output. |

## PITFALL MỚI (2026-07-18): `patch` fuzzy-match CẮT RỤNG đuôi dòng khi old/new dừng GIỮA dòng

Khi `patch` (mode=replace) dùng `old_string`/`new_string` dừng ở GIỮA 1 dòng (không capture hết phần sau của dòng đó), fuzzy matcher có thể match thành công NHƯNG thay thế dựa trên chuỗi cắt → **mất toàn bộ đuôi dòng**.

**Incident 2026-07-18:** Sửa WARREN_MEMORY.md xóa 2 dòng mem0. Ở 1 lần patch, con set `old_string` bắt đầu dòng `check_hours_alert() = 3 trigger ĐỘC LẬP` nhưng DỪNG tại `ĐỘC LẬP` (không lấy nốt `(Total / FOH+Bar / BOH=Leader+Cook) × 2 baselines:...`). `new_string` cũng dừng tại `ĐỘC LẬP`. Fuzzy match thành công → kết quả dòng bị cắt còn `...3 trigger ĐỘC LẬP`, mất hết phần trong ngoặc. Phải re-patch restore.

**SAFE PATTERN:**
- Luôn capture TOÀN BỘ dòng trong `old_string` (từ đầu `##`/`-` đến cuối dòng, kể cả phần sau điểm sửa).
- `new_string` cũng phải là dòng hoàn chỉnh (hoặc dòng mới hoàn chỉnh).
- SAU patch → `grep -n "từ_khóa_đuôi_dòng"` verify đuôi còn nguyên (vd grep `baselines: (1) LW same day` để chắc chắn không bị cắt).
- Nếu bị cắt → `git checkout -- <file>` (nếu tracked) rồi re-patch với full line, HOẶC dùng `write_file` merged content.
- Khi xóa 1 dòng nằm GIỮA 2 dòng khác → `old_string` PHẢI gồm cả dòng trước + dòng bị xóa + dòng sau (context đủ để unique), KHÔNG chỉ riêng dòng bị xóa rồi để đuôi trôi.
