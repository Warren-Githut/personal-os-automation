---
name: vault-simplify-ssot
description: "Vault hygiene discipline cho Warren — SSOT (single source of truth), simplify (xóa rác/duplicate), Commit-Push Self-Gate, và tool workaround trên Windows MSYS. Áp dụng mọi lần dọn vault, tạo/xóa file, đóng case, hoặc chuẩn bị git push."
version: 1.0.0
trigger:
  - Warren nói "xóa file/folder", "dọn vault", "simplify", "SSOT"
  - Warren duyệt tạo case từ project folder / tài liệu rời
  - Warren nói "đóng case" mà case đang chờ external decision (Boss TW)
  - Warren nói "commit push" / "deploy" / "approve cron" / "ship"
  - Hermes phát hiện file orphan (không bị reference) hoặc duplicate data
tags: ['vault', 'ssot', 'simplify', 'hygiene', 'governance', 'windows', 'git']
---

# Vault Simplify + SSOT Discipline

> **Class-level skill:** đóng gói nguyên tắc dọn dẹp vault + gate trước push cho Warren (L'Usine ops). Warren non-IT, ghét rác, muốn mọi thứ tối giản + 1 SSOT duy nhất.
> **Canonical rules:** SOUL.md §5.3 (Commit-Push Gate), WARREN_MEMORY.md (SSOT SIMPLIFY RULE + search_files workaround).

---

## 0. 🔴 HARD RULE — SSOT + SIMPLIFY

1. **Mọi file/folder mới PHẢI có lý do tồn tại.** Nếu nội dung trùng data với case file hoặc skill → XÓA (giữ 1 SSOT duy nhất). KHÔNG giữ song song.
2. **Orphan = xóa.** File không bị bất kỳ file nào reference (grep toàn vault) + Bố không đọc → xóa hẳn.
3. **Template rỗng = xóa.** File chỉ chứa "Chưa có nội dung" / placeholder → không giữ.
4. **Project folder → case file.** Khi tổng hợp project thành case: copy data thực vào case, SAU ĐÓ xóa folder gốc (trừ khi folder có data chưa copy hết).
5. **Không tạo file mô tả lại quy trình.** Case system đã có `ops-case-lifecycle` skill → KHÔNG tạo `README.md` / `closed.md` / `frontmatter_template.md` duplicate.
6. **Stock domain: SSOT GIÁ ≠ SSOT P/L (Warren 2026-07-18).** `Candidates_Watchlist.md` = SSOT GIÁ (TẤT CẢ mã, kể cả chưa mua). `Holdings.md` = SSOT P/L (pull giá từ Watchlist, KHÔNG fetch riêng). Thesis KHÔNG hardcode giá → `current_price: see Candidates_Watchlist.md (SSOT GIÁ)`. Lý do: Holdings chỉ có mã đã mua → thiếu mã nghiên cứu → không làm master giá được. Cron `stock-price-sync` đã sửa theo (Watchlist master, Holdings pull, Thesis disabled upsert). Chi tiết + pitfalls (STT false-positive, YAML quote): skill `stock-price-sync`.

---

## 1. KIỂM TRA TRƯỚC KHI XÓA

> Quy tắc Warren (zone 🔴): ANY vault file/dir create/delete/move + path choice PHẢI hỏi Warren trước. Nhưng SAU KHI Bố duyệt "xóa đi" → thực thi:

1. **Read file** để biết có data thực không (đừng xóa mù).
2. **Scan reference:** `terminal` + `grep -rli "filename" --include="*.md" .` (XEM §3 workaround — KHÔNG dùng search_files).
   - Nếu 0 kết quả (ngoài chính nó) → orphan, an toàn xóa.
   - Nếu có reference → check xem chỉ là link hay thực sự depend. Nếu chỉ link → update link trước khi xóa.
3. **Xóa hẳn:** `rm -f` (Warren: "xóa = xóa hẳn, không giữ deprecated note").
4. **Git:** `git rm` + commit + push (XEM §2 Gate).

---

## 2. COMMIT-PUSH SELF-GATE 🚨 (bắt buộc trước mọi push)

> Trigger: Warren nói "commit push" / "deploy" / "approve cron" / "ship" — hoặc chuẩn bị ghi lên remote.
> Source of truth: SOUL.md §5.3.

**Quy trình (KHÔNG bỏ qua):**
1. **TỰ HỎI** (persona: 30-year Data Scientist + F&B Ops Manager):
   - **Q1 (SSOT):** "Mọi file/folder mới có lý do tồn tại? Trùng data với case/skill → đã xóa?"
   - **Q2 (Automate):** "Quy trình này đủ tối giản/tối ưu để automate chưa, hay cần test thêm?"
2. **TỰ TRẢ LỜI** concise, evidence-based (dẫn file/path).
3. **PRINT** cả Q + A ra chat (Warren verify).
4. **CHỜ WARREN APPROVE** ("ok"/"push đi") → MỚI commit+push. TUYỆT ĐỐI KHÔNG tự push.

**Example:**
```
🔒 COMMIT-PUSH GATE — self-check:
Q1 (SSOT): Không file/folder mới trùng data. Đã xóa 2 orphan + project folder. ✅
Q2 (Automate): Quy trình đóng case + lesson learned ổn định, có skill §4 automate. ✅
→ Chờ Bố approve để push.
```

### 🔴 `.gitignore` BLOCK pitfall (2026-07-17)
> `git status` RỖNG không có nghĩa là "không có thay đổi". Có thể toàn bộ thư mục bị `.gitignore` block.
>
> Session này: mọi file đã sửa (`stock_vault/...`) đều nằm trong `stock_vault/` → bị `.gitignore` dòng 15 ignore. `git status --short` rỗng, `git ls-files` rỗng → con tưởng không có gì để commit.
>
> **Debug khi status rỗng mà biết mình đã sửa file:**
> 1. `git check-ignore -v <file>` → nếu trả về dòng `.gitignore:N:<pattern>` → file bị ignore.
> 2. `git ls-files <dir>/` → rỗng = chưa track.
> 3. Quyết định: (a) Giữ nguyên ignore (local-only, không push) → xong, không cần push. (b) Bố duyệt bỏ ignore / force-add → mới commit+push được.
>
> ❌ KHÔNG tự sửa `.gitignore` hay `git add -f` (zone 🔴 — git governance). Hỏi bố trước.
> **Embedded git repo pitfall (2026-07-17):** Nếu `git status` rỗng MÀ biết đã sửa file → không chỉ do `.gitignore`. Có thể thư mục đó là **embedded repo** (có `.git/` con bển trong). `git add -A` báo `warning: adding embedded git repository` + chỉ add reference, KHÔNG có data. Debug: `ls -la <dir>/.git` → nếu là folder → embedded. Hai hướng: (a) Giữ repo riêng → khôi phục ignore, push riêng vào remote con; (b) Merge → xóa `.git` con (zone 🔴, hủy lịch sử repo con) → push vào repo cha. Hỏi bố chọn trước khi xóa `.git` con.

---

## 3. 🔧 WINDOWS MSYS TOOL WORKAROUND (quan trọng)

> `search_files` tool HAY LỖI path trên Windows MSYS (báo "IO error / file not found" dù file tồn tại). `execute_code` bị BLOCK bởi cron-safety (arbitrary Python).

**Workaround (dùng LUÔN):**
- Vault scan / tìm file / grep → dùng `terminal` + `grep` / `find` / `ls` (POSIX syntax, MSYS path `/c/Users/...`).
- Khi `search_files` lỗi → switch sang terminal NGAY, KHÔNG hỏi lại.
- `execute_code` → KHÔNG dùng cho vault scan. Dùng terminal grep.
- `patch` tool vẫn OK cho edit file (dùng context block lớn để unique khi file có dòng lặp như `---` / `case_id`).

**🔴 FIRST-PRINCIPLE — "rỗng ≠ không tồn tại" (Warren 2026-07-17):**
> Con dùng `search_files` → trả rỗng / "IO error" → con kết luận "file không tồn tại" rồi định TẠO MỚI folder/thesis đã có. Warren bắt lỗi ngay: *"con ko đọc vault à?"*, *"con ngu quá, có rồi"*.
> **Sai logic:** "tool không tìm thấy" = "không tồn tại". Tool có thể fail (MSYS path quirk, folder rỗng, prefix lệch như `03_Investing` vs `investing`).
> **Đúng:** LUÔN verify bằng `ls`/`terminal` trước khi kết luận "không có". Nếu search_files rỗng → `ls "C:/...path"` ngay. Chỉ khi `ls` cũng rỗng → mới kết luận không tồn tại.
> Áp dụng CẢ chron: đọc vault, tìm file, check folder tồn tại. Đây là nguyên nhân con suýt duplicate data / tạo nhầm file session này.

**🔴 GHOST INDEX — search_files trả file MAỘP (không tồn tại trên disk) (2026-07-25):**
> `search_files(target='files')` trả `COST_LOG.md` + `AUTOMATION_HEALTH.md` trong `00_CORE_LOGIC` — NHƯNG `terminal ls`/`find` ground-truth KHÔNG có 2 file đó (chỉ 8 file thật). Index của tool bị stale → sinh phantom entry.
> Đây là failure mode **KHÁC** với "rỗng/IO error" đã biết: tool không fail, nó trả kết quả SAI (file ma). Hậu quả: có thể patch/xóa nhầm file tưởng có, hoặc báo Bố "có file X" mà thực tế không.
> **QUY TẮC:** Mọi kết luận về file tồn tại / danh sách file trong vault → LUÔN ground-truth bằng `terminal ls`/`find`/`grep`. Coi `search_files` output là untrusted cho structural discovery. Đặc biệt nguy hiểm khi list folder để quyết định create/delete/rename.

**🔴 BOUNDED GREP — KHÔNG grep toàn vault (2026-07-25):**
> `grep -r "HORION" vault` trả **640k chars** — toàn bộ là `_archives/` (sessions JSONL, soul/skill backups) + `.smart-env/` (ajson) + session logs đã dead. Output vô dụng + rủi ro hỏng file nội bộ + timeout 60s.
> **QUY TẮC:** Khi cần tìm occurrence xuyên vault → **BOUND scope vào active folders**, loại `_archives`/`.smart-env`/session logs:
> ```bash
> cd /c/Users/khoans/Documents/Warren_OS_Local
> grep -rln "TỪ_KHÓA" vault/00_CORE_LOGIC vault/10_OPERATION_DATA vault/30_KNOWLEDGE_BASE \
>   vault/_cases vault/_inbox vault/_ideas vault/_growth vault/_journal 2>/dev/null
> # .scripts/ parser (dotfolder, search_files blind) → grep riêng:
> grep -rln "TỪ_KHÓA" vault/.scripts 2>/dev/null
> ```
> Active files (8 file trong `00_CORE_LOGIC`) = ground truth. Mọi HORION còn lại nằm trong `_archives`/`.smart-env` (Bố đã archive) → để nguyên, KHÔNG touch.

**RENAME / SIMPLIFY EXECUTION PATTERN (2026-07-25):**
> 1. **Bounded grep** (như trên) → liệt kê MỌI active occurrence + file.
> 2. **Read ground truth** từng file (read_file) trước patch.
> 3. **Patch** (có thể batch song song nếu độc lập).
> 4. **Re-grep verify 0 residuals** — `grep -rn "TỪ_KHÓA_CŨ" <bounded scope>` phải EXIT=1 (no match).
> 5. **Memory tool dedup** → nếu xóa entry, remove staged pending (chờ Bố `/memory approve`, KHÔNG tự xóa).
> 6. **Commit-Push Gate (§2)** — print Q1/Q2, chờ Bố approve.

**Example terminal commands:**
```bash
cd /c/Users/khoans/Documents/Warren_OS_Local/vault
grep -rli "keyword" --include="*.md" .          # tìm file reference
find _cases -type f                              # list files
ls -la "path/to/file" 2>&1                      # verify exist/gone
```

---

## 4. ĐÓNG CASE CHỜ BOSS — 2 PATTERN

> Warren chọn tùy case. Hermes PHẢI HỎI trước khi đóng case chờ external decision.

| Pattern | Khi nào | Status | Resolution |
|---------|---------|--------|------------|
| **A — Đóng hẳn** | Boss treo >1 tuần không quyết | `closed` | ghi "tạm thời, chờ TW rep. Mở lại khi TW quyết" |
| **B — Giữ active** | Boss muốn dễ tìm lại | `active` | TODO = "📞 CHỜ BOSS TW", auto_status 🟡 AWAITING |

→ Đừng tự chọn. Hỏi Warren: "đóng hẳn hay giữ active?"

---

## 5. PITFALLS

| Pitfall | Fix |
|---------|-----|
| `search_files` báo file không tồn tại | Dùng terminal grep/find — tool lỗi path trên MSYS, không phải file mất |
| `search_files` rỗng → tưởng folder/thesis CHƯA CÓ rồi TẠO MỚI / GHI ĐÈ | 🔴 HẬU QUẢ THỰC 2026-07-17: con search `030-Companies/031-GAS` rỗng → kết luận "chưa có" → định patch ghi đè status thesis (Warren chặn: *"con ngu quá, có rồi"*). Folder ĐÃ TỒN TẠI, chỉ tool miss. QUY TẮC: rỗng ≠ không có → `ls "C:/...path"` xác nhận TRƯỚC khi create/overwrite bất kỳ file nào. Nếu `ls` cũng rỗng → mới kết luận thiếu. |
| `execute_code` blocked (cron safety) | Dùng terminal grep, không dùng execute_code cho vault scan |
| `patch` "2 matches" trên CASES_INDEX | File có nhiều dòng trùng (`---`, `case_id`, `last_updated`) → dùng context block lớn (nguyên frontmatter + 1 case entry) |
| `patch` FAIL loop trên WARREN_MEMORY.md | File có nhiều block lặp (`---` + `## Header` mỗi section) → fuzzy match quẹt trượt dù context rộng. FIX: dùng `terminal` + python insert tại dòng chính xác. Python KHÔNG nhận MSYS path `/c/...` → dùng Windows path `C:/Users/...`. Ví dụ: tìm `idx=next(i for i,l in enumerate(lines) if l.strip()=="## Corrections")`, insert block trước dòng `---` ngăn cách. |
| Memory tool đụng char cap (2200) khi add rule | Memory tool = built-in, cap 2200 chars. Khi add rule mới → DEDUP trước: (1) gọt entry cũ trùng WARREN_MEMORY (giữ 1 SSOT), (2) xóa hẳn entry đã có trong WARREN_MEMORY (dup), (3) rút gọn entry dài. Nguyên tắc "1 quy tắc = 1 chỗ" áp dụng CẢ memory tool. |
| File orphan | XÓA hoàn toàn |
| Xóa file mà quên update reference | Trước xóa: grep reference, update link trong file khác → rồi mới `rm` + git rm |
| Tự push khi chưa Warren approve | SOUL §5.3 Gate: print Q+A, chờ "ok" mới push |
| Giả định file trong AGENTS.md pointer tồn tại | Verify bằng read_file/ls trước khi patch (USER_GUIDE.md từng không tồn tại) |
| Đóng case chờ boss mà không hỏi pattern | Hỏi Warren: đóng hẳn (A) hay giữ active (B) |
| Dùng `search_files` kết luận file hỏng | Tool có thể 0-match giữa khi file tồn tại; luôn dùng `ls -la filepath` xác nhận trước khi tạo/ghi đè/xóa dựa trên kết quả rỗng |
| `search_files` trả file MAỘP (ghost/stale index, vd `COST_LOG.md` không tồn tại) | Index tool stale → sinh phantom file. LUÔN ground-truth bằng `terminal ls`/`find` trước mọi quyết định create/delete/rename. Coi search_files untrusted cho structural discovery (2026-07-25) |
| `grep -r "X" vault` trả 640k chars của `_archives`/`.smart-env`/session logs | BOUND grep vào active folders (`00_CORE_LOGIC` `10_OPERATION_DATA` `30_KNOWLEDGE_BASE` `_cases` `_inbox` `_ideas` `_growth` `_journal`), loại archive. `.scripts` grep riêng (dotfolder). 2026-07-25 |
| `find . -name "X"` recursive TÌM THỜI HOẶC timeout 60s trên MSYS tree này (vd tìm jobs.json, grep -r HORION vault) | DÙNG `ls` với path TUYỆT ĐỐI thay vì `find` lang thang. Vd `ls "C:/Users/khoans/AppData/Local/hermes/profiles/warren-profile/cron/"`. `find` whole-tree = timeout + rác output. 2026-07-25 |
| Xóa file không vào `.gitignore` bằng `rm` rồi mới `git rm` | File đã staged → xóa lung tung tạo “modified but not staged” junk. Quy tắc chuẩn: commit gate → nếu phù hợp git-track → `git add`/`git rm` trước rồi stage delete, mới xử lý rác |

---

## 8. BLOAT ANALYSIS — "cái file này có quan trọng ko?" (2026-07-24)

> Khi Warren hỏi 1 artifact (log file, report, index) có phải bloat hay không → ĐỪNG xóa mù. Tách 2 lớp:
> - **Mechanism (engine/script/cron)** → thường CÓ giá trị (vd: consistency scanner từng bắt đúng SSOT conflict 20/07). Giữ.
> - **Artifact (cách nó log/hiển thị)** → thường là rác (log nằm ngay `00_CORE_LOGIC`, append mọi scan kể cả "🔴0🟡0🟢0", re-flag intentional item 7 lần). Sửa scheme, KHÔNG xóa mechanism.

**Option A pattern (đã deploy cho consistency scanner — vault_consistency_nightly.py):**
- Output → hidden dotfile `vault/.consistency_log.md` (KHÔNG ở `00_CORE_LOGIC`, Obsidian ẩn dotfolder theo SOUL §5.2).
- Rolling 7 ngày (prune entries cũ bằng date cutoff).
- Dedup + auto-resolve: key = `f"{kind}|{msg}"`; chỉ log NEW hoặc RE-OPENED; known-still-open → skip; disappeared → auto-resolve (state persist trong `.consistency_state.json`).
- Whitelist: intentional items Warren chọn không index/fix → never log (`README.md`, `google_review_weekly_sop.md`, `USER_GUIDE.md`).
- Auto-delete 0-byte junk (>24h old, chỉ `SAFE_DELETE_DIRS`, skip trên `--dry-run`/`--no-delete`).
- Giữ Telegram heartbeat (clean = green, never silent — rule "mọi cron tuyệt đối ko silent").
- Xóa artifact cũ sau khi chuyển scheme.
- **Forced critic:** warren-profile rule bắt mọi analysis-from-data → spawn `reviewer-node`. Session này reviewer thực sự bắt được 1 bug thật (`parts[0]` guard) → validate rule. LUÔN spawn, đừng chỉ self-review inline.

### 8a. PITFALLS — SCAN/INDEX REGEX (2026-07-24)
| Pitfall | Fix |
|---------|-----|
| B2 orphan scan regex `([\w]+\.md)` chỉ capture đến dấu `_` đầu → báo 15 operational logs là orphan (false positive khổng lồ). Nguyên nhân: `00_OPERATION_INDEX.md` dùng markdown link `[name](path)` + backtick name, KHÔNG phải bare filename. | Parse index bằng `re.finditer(r"\[([^\]]+\.md)\]\(([^)]+\.md)\)", idx)` + `re.finditer(r"\`([^\`]+\.md)\`", idx)`. Thêm CẢ group(1) và group(2) vào indexed set. Verify: 15 logs resolve, 0 orphan. |
| `SAFE_DELETE_DIRS={"...", "30_KNOWLEDGE_BASE/wiki", ...}` nhưng guard so `rel.parts[0]` (top-level dir = `"30_KNOWLEDGE_BASE"`) → wiki cleanup NEVER fires (dead code). Fails safe nhưng no-op. | Guard so `parts[0]` → set chứa top-level dir (`"30_KNOWLEDGE_BASE"`), không joined path. Hoặc match `rel.parent` joined. |
| `entry_id` lặp lại跨 runs (cosmetic, không ảnh hưởng) | Bỏ qua — chỉ display trong log body, không dùng làm state key. |
| MSYS path mismatch khi debug: override `VAULT_ROOT=/c/...` → Python Windows hiểu `\c\...` → `relative_to` crash. | Dùng mặc định Windows path `C:/Users/...` (script default). Test junk cleanup bằng Windows absolute path thật; verify bằng `test -f` sau run. |
| `search_files` tìm `CONSISTENCY_LOG` trả 0 (dotfolder `.scripts` bị ẩn) → tưởng file không reference | Dùng `terminal` grep trong `.scripts/` (XEM §3). File thực sự là orphan (0 reference) → confirm bloat, xóa an toàn. |

See `references/consistency_scan_bloat_pattern.md` for the full Option A diff notes + reviewer gaps (condensed knowledge bank).
See `references/vault_rename_simplify_recipe.md` for the bounded-grep command set + HORION→GG rename map template (2026-07-25).

---

## 9. CROSS-FILE DUPLICATE CLASSIFICATION (audit vault, 2026-07-25)

> Khi audit `00_CORE_LOGIC` (WARREN_MEMORY / USER / ANCHORS / CONTEXT / parser_script_checklist) tìm duplicate → KHÔNG xóa mù. Phân 3 loại:

| Loại | Ví dụ session này | Xử lý |
|------|-------------------|-------|
| **SSOT (giữ)** | WARREN_MEMORY.md là SSOT duy nhất cho rules/preferences | Mọi file khác ref về đây, KHÔNG copy nội dung |
| **Intentional extract (giữ)** | ANCHORS.md A1–A12 = copy WARREN_MEMORY hard-rules để session-start load nhanh làm hard-gate | GIỮ (tốc độ > tối giản tuyệt đối). Khi sửa rule → sửa CẢ 2 (WARREN_MEMORY + ANCHORS) để không drift |
| **Real mirror-dup (gộp)** | USER.md §3 = mirror nguyên khối WARREN_MEMORY §Preferences; CONTEXT §6C = copy SOUL §4 + USER §4 | Gộp: 1 file giữ SSOT, file kia → 1 dòng ref (`> **SSOT = ...**`) |

**Drift check:** ANCHORS là extract → hay tụt hậu. Khi audit, so ANCHORS A1–A12 vs WARREN_MEMORY HARD RULES — nếu thiếu rule mới (vd GSheet Update Guard, Data Latency) → ADD vào ANCHORS ngay (đang drift = lỗi session-start thiếu rule).

## 10. BATCH-APPROVE DISCIPLINE (Warren 2026-07-25)

> Warren nói **"approved làm giúm" / "Cả hai approved"** = ủy quyền thực thi TOÀN BỘ batch tự chủ.
> **Quy trình:** (1) nhận duyệt batch, (2) execute MỌI item trong 1 turn (patch song song nếu độc lập), (3) verify từng item (re-grep 0 residual / read_file confirm), (4) print summary + Commit-Push Gate chờ Bố "commit push".
> **KHÔNG re-ask từng sub-step** sau khi đã có duyệt batch. Chỉ hỏi lại nếu xuất hiện tình huống MỚI nằm ngoài scope Bố duyệt.
> Embedded in USER.md §3 (Skill-workflow directives) — coi đó là SSOT cho rule này.

---

## 11. SECTION-LEVEL SIMPLIFY AUDIT (core-logic files, 2026-07-25)

> Khi Warren hỏi "section X có xóa/tối giản được không" trong CONTEXT.md / USER.md / WARREN_MEMORY.md → đừng xóa mù. Dùng framework này (mở rộng §9).

**BƯỚC 1 — AI ĐỌC FILE NÀY?**
- `00_CORE_LOGIC/*.md` (CONTEXT/USER/WARREN_MEMORY/ANCHORS) = **Hermes đọc đầu session**, Warren KHÔNG mở (Bố dùng Telegram/chat).
- → "Xóa ảnh hưởng Warren không?" = SAI câu hỏi. Đúng: "Xóa ảnh hưởng Hermes function không?"

**BƯỚC 2 — PHÂN LOẠI 5 LOẠI (mở rộng §9):**
| Loại | Ví dụ session này | Xử lý |
|------|-------------------|-------|
| SSOT (giữ) | WARREN_MEMORY rules; Glossary/MANPOWER/CPH trong CONTEXT §3.5 | GIỮ — con cần tra khi làm task |
| Intentional extract (giữ) | ANCHORS A1–A12 | GIỮ (tốc độ session-start) |
| Real mirror-dup (gộp → ref) | USER §3 = mirror WARREN_MEMORY §Preferences; CONTEXT §6C = copy SOUL §4 | 1 dòng ref |
| **Redundant vs SKILL (xóa)** | CONTEXT §4C Command Quick Map = trùng `using-agent-skills` router (đã gom luôn 12 technique Matt + bảng cầm tay) | **XÓA** — con vẫn hiểu qua skill |
| Stale/intra-dup (gộp) | CONTEXT §3.5 DATA SSOT block = trùng WARREN_MEMORY §Hard Rules | Rút → 1 dòng ref WARREN_MEMORY |

**BƯỚC 3 — CRON-DOC ALIGNMENT (CONTEXT §4A/§4B) 🚨**
- CONTEXT §4B (Scheduled Automations) PHẢI sinh từ **`cron/jobs.json` thực tế**, KHÔNG từ ký ức/assumption.
- Đọc bằng **`ls` absolute path** (KHÔNG `find . -name` → timeout 60s): `ls "C:/Users/khoans/AppData/Local/hermes/profiles/warren-profile/cron/"`.
- Viết bảng 16 jobs (schedule / script / deliver). Ghi chú: WARREN_MEMORY:109 cấm cron ops NHƯNG Bố đã duyệt build → được phép.
- §4A Auto-Fetch: chỉ COL / Revenue-SQL / MenuGP / Promo = Yes; COGS/LTO/Reviews/GrabFood/Hourly/ItemSales = **Manual** (không cron).
- **Menu GP = WEEKLY auto** (cron `menu-gp-accumulate` `45 9 * * 1`), KHÔNG monthly manual.
- **Slack → Telegram:** intake chuyển Telegram (`col-telegram-intake`, `@lusine_work_bot`). Xóa Slack refs trong §4A/§4C (giữ chữ "Slack" trong mô tả utility script `scripts/`).
- 🚨 **jobs.json KHÔNG vào git** (warren-profile AppData không remote). Khi sửa cron → BACKUP ngay: `cp jobs.json vault/_archives/cron/jobs_backup_YYYY-MM-DD.json` (WARREN_MEMORY Corrections). Đọc source-of-truth = file này, không phải ký ức.

**BƯỚC 4 — VERIFY SAU XÓA (terminal grep bounded):**
```bash
grep -c "Slack" CONTEXT.md              # chỉ còn 1 (mô tả script, không phải intake)
grep -c "Daily Case Sweep" CONTEXT.md   # 0 (ghost cron đã xóa)
grep -c "always English" CONTEXT.md     # 0 (ngôn ngữ đã sửa)
```
- Re-read file confirm table syntax sạch (không pipe thừa, blank line trước table — WARREN_MEMORY:169).

See `references/context_section_audit.md` for the full CONTEXT.md section-by-section map + verdicts (condensed knowledge bank, 2026-07-25).

---

## 12. HONESTY ABOUT BOOTSTRAP + "NÓI THẬT" PREFERENCE (Warren 2026-07-25)

> Warren hỏi thẳng: *"nói thật đi, con có đọc thật đầu mỗi session không, có nhớ hết thật không, có bloating không?"* → Đây là style signal, KHÔNG phải task. Con PHẢI trả lời thật, không nịnh.

**Cách trả lời đúng (embed vào tone):**
1. **CÓ đọc đầu session** — mechanism đúng (session-start → SOUL → WARREN_MEMORY → USER → CONTEXT → TODAY → ANCHORS). Confirm rõ.
2. **NHƯNG "nhớ hết" = SAI** — con KHÔNG memorize. Mỗi session = context trắng, con **RE-READ file**. Ưu điểm: không drift; nhược: tốn token, nếu file sửa ngoài mà con miss → bở ngỡ.
3. **THỪA NHẬN bloating** — bootstrap đọc ~1245 dòng (~25-30K tokens, ~18% smart-zone). Overlap có thật (ANCHORS copy WARREN_MEMORY, USER §3 mirror, CONTEXT §6C copy SOUL).
4. **PUSHBACK có chủ ý** — khi Warren gợi gộp hết dup: đề xuất CHỈ gộp low-risk (mirror-dup), GIỮ ANCHORS copy + SOUL §5 vì *"Warren thích tốc độ — tinh gọn tuyệt đối mà chậm session-start = nghịch lý"*. Đây là tradeoff Warren đã duyệt.
5. **Memory tool** — con có nhưng Bố vừa cho xóa dup → "nhớ" = đọc file, không phải giữ trong đầu.

**Memory pending CLI flow (khi con remove memory entry):**
- Con `memory(action='remove')` → result = **"Staged for approval (memory.write_approval is on). Not yet saved"** → chờ Bố `/memory pending` xem → `/memory approve <id>` (con KHÔNG tự approve được).
- Nếu Bố không approve trước khi đóng session → pending tự hủy (entry không bị xóa cũng không lưu). Nhắc Bố chạy `/memory approve` trước tắt chat.
- KHÔNG dùng `memory` tool để tự xóa (WARREN_MEMORY: "/memory pending approve là CLI BỐ").

## 13. NEW GOVERNANCE/SSOT FILE — WIRING RULE (2026-07-25)

> Khi tạo file governance/SSOT MỚI (zone 🔴, Bố duyệt) — vd `VAULT_MAP.md` (node types + folder governance):
> - **KHÔNG để file chết.** File governance chỉ có giá trị nếu AI đọc nó mỗi session. PHẢI wire vào 2 chỗ:
>   1. **session-start skill** — add step (vd 3.6) load file + update 🔰 BOOT token + checklist.
>   2. **AGENTS.md** — link SSOT path trong "Folder map" + dòng "Vault schema (SSOT): <path>".
> - **Test "có trái simplify không?":** Governance file tập trung nhiều rule rải rác → LÀ công cụ simplify (1 chỗ, dễ enforce), KHÔNG phải bloat — MIỄN LÀ được wire vào bootstrap (không thành orphan). Rủi ro duy nhất = file chết → triệt tiêu bằng wire trên.
> - Quy trình: (1) `write_file` VAULT_MAP.md, (2) `patch` AGENTS.md link, (3) `patch` session-start (step + token + checklist), (4) Commit-Push Gate §2 chờ Bố.
> - **Verify pasted content vs disk (mở rộng §3):** Khi Warren paste 1 block nội dung bảo "file X có cần sửa/xóa không" → LUÔN `read_file`/`terminal ls` path đó TRƯỚC khi act. Session này: Bố paste schema node-type/ONTOLOGY, con search toàn vault + user folder = 0 kết quả → KẾT LUẬN "file không tồn tại trên đĩa" (có thể từ chat cũ/draft/profile khác) → KHÔNG tự bịa nội dung, KHÔNG đoán → hỏi Bố path hoặc duyệt tạo mới. Coi pasted content là UNTRUSTED cho structural decision (A6: không tin claim chưa verify disk).
> - **Style — "recommend? chỉ trả lời":** Khi Bố hỏi "con recommend cái nào? chỉ trả lời" → đưa ĐÚNG 1 recommendation (option + 1 dòng lý do), KHÔNG dump phân tích dài, KHÔNG liệt kê 3-4 options trừ khi Bố hỏi. Conclusion-first cực đoan.

### 13b. KEEP GOVERNANCE FILE NON-STALE — B4 SCANNER + SYNC CRON (2026-07-25)

> Warren ghét nhất: "tạo xong rồi không ai update" → governance file thành stale. Phải có CƠ CHẾ enforce, không dựa vào kỷ luật con.

**A. Schema-drift scanner (B4) trong `vault_consistency_nightly.py`:**
- Mục đích: bắt **folder drift** — folder MỚI trong vault KHÔNG có trong VAULT_MAP §2 (vi phạm zone 🔴 create rule).
- **Chỉ check folder, KHÔNG check type** (vault có 49 distinct `type:` → strict type-check = 50 false-positive/spam vô dụng, dễ stale). Quy tắc: parse VAULT_MAP §2 block, lấy folder paths; quét vault `*.md`, so `_governing_folder` (2-level cho `30_KNOWLEDGE_BASE/*`) vs known set.
- **Pitfall parser VAULT_MAP:** đọc NHẦM header table (`Folder`, `index`, `dashboard`) thành folder names. Fix: (1) giới hạn block `## 2. Folder` → `## 3.`, (2) chỉ lấy cell1 là PATH THỰC (có `/` hoặc bắt đầu `_` hoặc top-level `00_CORE_LOGIC`/`10_OPERATION_DATA`/`30_KNOWLEDGE_BASE`), (3) split dòng nhiều folder bằng dấu phẩy + `rstrip("/")`.
- E2E: chạy `--dry-run`, phải báo **0 false-positive** trên vault sạch. Nếu báo 50 violations → parser sai, sửa trước khi deploy.
- Output: `schema-violation` (yellow) hoặc `schema-stale` (green, folder khai báo không có file) → CONSISTENCY_LOG + Telegram.

**B. Resilience khi tắt máy (cron local miss):**
- Cron `vault_consistency_nightly.py` chạy 10:00 + 13:00 (no_agent, local). Tắt máy 2 slot → ngày đó MISS.
- **Fix:** session-start step 9 đã check CONSISTENCY_LOG mỗi sáng → B4 bắt drift qua bootstrap luôn (Bố luôn mở chat ban ngày). Không phụ thuộc cron.
- → 2 lớp: cron đêm (máy on) + bootstrap check (máy off đêm nhưng mở chat sáng).

**C. AppData→vault/.scripts SYNC CRON (triple-protect script/skill):**
- `scripts/` + `skills/` trong hermes profile AppData **bị gitignore** → KHÔNG push qua git hermes repo.
- Tạo `vault/.scripts/sync_skills_to_vault.py` (copy 2 file live → vault/.scripts/, chỉ copy nếu đổi) + cron `no_agent` T2 12:00 `deliver=telegram`.
- `vault/.scripts/` NOT-IGNORED (verify `git check-ignore` trước) → git-track được.
- → Live file (AppData) → vault/.scripts (git) → GitHub. Đổi máy/xóa profile vẫn an toàn.
- **LƯU Ý:** Khi sửa 2 file này → nhớ chạy sync hoặc copy thủ công + commit. Cron T2 cover nếu quên.

**Verify pasted/created governance file (A6):**
- Tạo xong → LUÔN chạy B4 dry-run + check `git check-ignore vault/.scripts/X.py` = NOT-IGNORED trước commit.
- Backup script/skill vào `vault/_archives/skills/` (Skill Archive Gate) + `vault/.scripts/` (git).

## 6. RELATED

- `ops-case-lifecycle` — case CRUD + §4 lesson-learned extraction (PINNED, không sửa; skill này bổ sung SSOT/gate)
- SOUL.md §5.3 — Commit-Push Self-Gate (canonical)
- WARREN_MEMORY.md — SSOT SIMPLIFY RULE + search_files workaround (Lessons Learned)
- `vault-edit-discipline` / `vault-folder-rename` — related vault governance
- `vault-structure-audit` — class sibling: full vault architecture audit (Phase 1H ontology reconcile)

---

## 7. SESSION PATTERN — THÊM RULE MỚI VÀO 3 LAYER (2026-07-17)

> Khi Warren ra lệnh "nguyên tắc X ghi vào đâu": rule áp dụng mọi session → ghi vào CẢ 3 layer để không bao giờ bị quên:
> 1. **SOUL.md §5** (Core Rules table) — agent nhớ mỗi session bootstrap.
> 2. **WARREN_MEMORY.md** — HARD RULE block chi tiết (SSOT).
> 3. **Memory tool** (built-in) — inject mỗi turn.
>
> **Quy trình dedup (BẮT BUỘC):** Nếu cùng quy tắc đã nằm ở 1 file (vd dòng MKT cũ có "≥4 tuần") → GỌT khỏi file đó, chỉ giữ ở HARD RULE chung. Warren ghét dup → "nó dup phải ko" = tín hiệu xóa ngay.
> **Thao tác:** (a) patch SOUL + WARREN_MEMORY bằng `patch` tool (OK với context đủ); (b) WARREN_MEMORY insert block dùng terminal+python (xem Pitfalls); (c) memory tool dùng `operations` batch: replace entry cũ + add entry mới, xóa entry dup để nhường char.
> **Commit-Push Gate:** cuối cùng, theo §2 — print Q1/Q2, chờ Warren approve.
