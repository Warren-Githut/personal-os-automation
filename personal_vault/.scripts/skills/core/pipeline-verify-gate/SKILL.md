---
name: pipeline-verify-gate
description: "Class-level discipline cho mọi parser/skill/script/pipeline mới — E2E thực tế TRƯỚC push, verify dùng NGUỒN ĐỘC LẬP (KHÔNG circular), aggregation formula toán học đúng, major output qua reviewer-node, và tự-react hook (không đợi manual trigger). Từ Warren 2026-07-23 COL session."
type: skill
version: 1.0
status: active
applies_to: ["Hermes Desktop"]
---

# pipeline-verify-gate — E2E + Independent Verify Discipline

> Warren 2026-07-23 (COL pipeline session): "test phải so với NGUỒN ĐỘC LẬP, không tự tính lại bằng chính logic cũ" + "verify gate đó phải được làm từ Reviewer node cho khách quan".

Áp dụng cho MỌI parser / skill / script / pipeline — không chỉ COL.

## Hard Rules (4 gates bắt buộc)

### Gate 1 — E2E TRƯỚC PUSH (Warren directive)
Không báo "xong" / không push / không commit khi chưa chạy thực tế trên **input THẬT** do Warren trigger.
- Unit test / battle-test / code-review một mình KHÔNG đủ.
- Chỉ E2E mới lộ bug class: false-positive override (P15), missing approval hook (P16), silent Telegram gap (P19), circular verify (P11/P12).
- Warren gửi input thật + trigger thật → mới claim done.

### Gate 2 — INDEPENDENT VERIFY, KHÔNG CIRCULAR (ANCHORS A9)
Verify gate KHÔNG được so với output của chính pipeline đang test.
- ❌ SAI: COL parser append GSheet → "verify" bằng đọc lại row GSheet vừa append (circular, chỉ confirm chính write).
- ✅ ĐÚNG: Cross-check nguồn ĐỘC LẬP — cùng brain-dump `Σ(Guest_i×AC_i)` vs `Σ(Net Revenue)`; hoặc 2nd independent parse path.
- Nếu chỉ có output tự pipeline → verify VOID, KHÔNG claim PASS.

### Gate 3 — FORMULA CORRECTNESS (reviewer-node caught)
Aggregation check dùng toán học đúng:
- ❌ `(ΣGuest)×mean(AC)` → covariance artifact → phantom drift trên data consistent hoàn toàn.
- ✅ `Σ(Guest_i×AC_i)` per-element sum.
- Verify report PHẢI show số 2 bên, không chỉ PASS/FAIL (để formula bug visible).

### Gate 4 — REVIEWER-NODE cho verify gate / major output (ANCHORS A10)
Self-written self-verified có blind spot. Spawn `reviewer-node` (fresh context) review output + checklist TRƯỚC deliver.
- Session này reviewer bắt đc phantom-drift formula error author bỏ sót.
- Reviewer MUST check: (a) nguồn thực sự independent (không circular), (b) aggregation đúng, (c) verify confirm NỘI DUNG không chỉ tồn tại.

### Gate 5 — HOOK GAP = "con không phản ứng"
Khi Warren nói "con ko phản ứng gì" → NGHĨ HOOK/TRIGGER GAP TRƯỚC, không phải code bug.
- Warren expect bot TỰ react (gõ OK → tự append + gửi confirm Telegram).
- Nếu chỉ cron khung hẹp (09:00/10:00) → ngoài khung = chết.
- Fix: intake poll đủ dày (mỗi 15p trong giờ làm việc) + bắt approval keyword + gửi kết quả ngược lại.

### Gate 6 — AUDIT EXISTING CRONS cho verifier gaps (2026-07-25 Context/Loop Engineering session)
Khi Bố yêu cầu audit cron/automation cho "verifier gate" (bài @vartekxx: *"Without verifier = agent đồng tình với chính nó on repeat"*):
- **Method (đọc script THẬT, KHÔNG claim absent):** với mỗi `no_agent` job → `grep -inE "verify|assert|raise|sys.exit|except" <script>`; với LLM cron → đọc prompt preview có bước check rõ ràng không.
- **Phân loại:** ✅ cứng (hard exit khi data sai) · 🟡 low-risk (backup/draft-only) · ❌ GAP (nuốt lỗi → silent wrong).
- **CHỐT số: KHÔNG gán nhãn "đã có verifier" cho job intake nếu verifier nằm ở pipeline DOWNSTREAM.** Intake poller (vd `col_telegram_intake.py`, `revweek_telegram_intake.py`) thường ZERO verify — verify thật sống ở tầng approve/pipeline. Ghi rõ "verify downstream, chưa spot-check tại script", KHÔNG credit job intake.
- **Luôn qua reviewer-node (A10)** khi audit — critic bắt đc blind spot con bỏ sót (xem references).

## Checklist (dán vào bất kỳ skill class nào khi tạo pipeline mới)
- [ ] E2E chạy thực tế trên input thật trước push?
- [ ] Verify gate dùng nguồn ĐỘC LẬP (A9)? Không circular?
- [ ] Aggregation formula toán học đúng (per-element sum)?
- [ ] Major output qua reviewer-node (A10)?
- [ ] Tự react được không (hook/cron/trigger) hay cần manual? Nếu manual → thiếu hook.

## Integration
- Chạy SAU `verify-parser-output` (layer 2) cho parser.
- Chạy SAU mọi build pipeline trước git-push-self-gate.
- Pair với `reviewer-node` (Gate 4) + `verify-parser-output` (Gate 2/3).
- Warren-profile carries its own copy; applies mọi profile.

## 🔧 Post-Fix Per-Slice Review Loop (Warren directive 2026-07-25)

> Sau khi fix xong 1 bug parser/script vault, Bố bắt BUỘC chạy 3 review skills
> như **independent per-slice passes** — KHÔNG gộp 1 pass chung.

Quy trình mỗi slice (1 fix = 1 slice):
1. **Patch** file (theo `parser_script_checklist.md` gate ở ANCHORS 3.5).
2. **`code-review-and-quality`** — 5-axis review slice đó.
3. **`improve-codebase-architecture`** — scope-before-scan (YAGNI): grep cùng
   bug-class khắp repo (defense-in-depth), KHÔNG quét toàn bộ.
4. **`code-simplification`** — simplify slice; sau mọi move dòng trong loop, re-check
   indent (dòng `+=`/`.append()` lọt ra ngoài `for` → output truncate silently).
5. **Verify độc lập** mỗi slice (pytest + real-input E2E) trước khi chốt.
6. **`reviewer-node`** (ANCHORS A10) — subagent fresh context check.
7. **Archive backup** changed scripts → `vault/_archives/skills/`.

**Hard rule:** One fix = one slice. Patch → pytest slice → review → simplify → next.
KHÔNG batch nhiều simplify chưa test.

**Class lessons từ COL parser 2026-07-25** (format-gap + fallback scope-blindness +
`load_history` dict gotcha): xem `references/warren-col-parser-fix-2026-07-25.md`.
Tóm tắt:
- Parser fallback derive value TỪ TEXT phải **scope theo store-section**, không global
  first-match (lộ data cross-store).
- Verify gate có thể **false-alarm khi parser bể** — sanity-check per-store output
  trước tin warning.
- **Match cấu trúc trả về thật** (`load_history` = dict, không list).

### Gate 7 — NUMERIC / AGGREGATION REVIEW of a computed metric (review discipline)

When reviewing a change that adds/alters a **computed metric shown in a dashboard / Telegram brief / markdown table** (revenue averages, WoW/MoM %, 4-week rolling baselines, System totals), a green test run is NOT enough. Apply by hand (real session: 4wAvg review 2026-07-26 on `cases_parser.py` / `send_today_brief.py` / `gen_today.py`):

1. **Rolling-window leakage.** Baseline must use PRIOR periods only, offsets distinct. CORRECT: `avg of back in (7,14,21,28)` where `latest_date` = latest *prior* day (back-7 already last week) → 4 prior same-weekdays. WRONG: if anchor were *today*, back-7 leaks current week. Confirm anchor vs "latest prior" definition.
2. **Hand-recompute every displayed aggregate** from raw inputs (Gate 2: don't trust author's recompute). Cross-assert sum-of-stores == System total for EACH metric (rev, LW, 4wAvg). One slip in a System line ships silently.
3. **Markdown table column-count audit.** Count `|` in header, every data row, AND separator — all must match. 1-col mismatch silently shifts every cell in that column. Verify against the generated row f-string, field by field.
4. **Partial-data / min-window guards.** Count `< required window` (e.g. `< 4` prior weeks) → render `—` / skip, NOT a fake `0.0` average. Watch for a numeric value printed *next to* a "missing data" label = misleading pseudo-zero.
5. **Audit the E2E harness's own assertions** (not just PASS/FAIL). `has_col = "x" in y or True` → permanent no-op → false green. Recompute via the SAME function it tests → circular (Gate 2). Require raw-input-independent recompute, or treat PASS as untrusted.

### Locator Pitfall — hidden dotfolders NOT indexed by search_files/ripgrep

This vault keeps runnable Python in **hidden dotfolders**: `vault/.scripts/`, `vault/10_OPERATION_DATA/.scripts/`, `._accumulation/`. `search_files` (ripgrep) **cannot read them** → `IO error ... os error 2/3` for both content and files queries on `vault/.scripts/`. A review session can waste a round concluding a file is missing when it IS there.
- Symptom: you know `cases_parser.py` exists but `search_files` says "total_count: 0" / errors. Don't conclude missing.
- Fix: `terminal` grep (`grep -rn "def foo" /c/Users/.../vault/.scripts/`) or `read_file` with explicit path. `read_file` works on dotfolders; only `search_files`/rg fails.
- The task's *stated* path is usually right (here `vault/.scripts/` was correct) — the failure is the **tool**, not the path. Don't re-guess the directory.

## Pitfalls (real, 2026-07-23 COL session)
- Circular verify lọt qua nếu không check nguồn (read-back GSheet = output tự pipeline → void).
- Phantom drift từ sai công thức `(ΣGuest)×mean(AC)` ≠ `Σ(Guest_i×AC_i)`.
- Existence ≠ correctness (read-back tìm thấy row ≠ row đúng → phải confirm content).
- "Con không phản ứng" thường là hook gap, không phải logic bug.

## Pitfalls (thêm, 2026-07-24 revenue-pipeline session)
- **E2E cần input THẬT với parser OCR/layout-specific:** Ảnh AI giả (FAL) hoặc 1x1 PNG KHÔNG khớp layout PowerBI thật → liteparse đọc được text nhưng regex parser (tìm "Net Revenue" + 4 số cùng dòng) không match → parser đúng từ chối. KHÔNG thể happy-path E2E bằng ảnh giả. Fix: verify mọi failure path (test-json, verify-fail, OCR-fail, cron run) bằng fixture; happy-path GHI SSOT THẬT phải chờ Warren gửi ảnh PowerBI T2 thật. Đừng claim "done" khi chưa E2E input thật (Gate 1).
- **Test mode PHẢI --dry:** Orchestrator `--test` gọi parser `--test-json` PHẢI ép `--dry` xuống parser. Thiếu → test run ghi đè block giả vào SSOT thật + overwrite `latest_week_range` (con lật 1 block W29 giả, revert bằng `git checkout`). Rule: mọi `--test` mode KHÔNG được chạm vault thật.
- **Orchestrator exit-code mapping:** Wrapper gọi parser map exit code riêng → 🔴 riêng: `1`=THIẾU ẢNH/SAI LỆNH, `2`=VERIFY FAIL (L1/L2/L3), `4`=OCR FAIL (ảnh không đọc được). KHÔNG gộp chung "lỗi". Parser crash uncaught (RuntimeError) → exit 1 nhầm thành THIẾU ẢNH.
- **Telegram intake persist-partial:** Warren gửi 4 ảnh rải rác → save ảnh NGAY khi nhận (`raw/revenue_screenshots/{week}_{slot}.png`), đếm đủ 4 mới chạy. KHÔNG buffer file_id trong memory chờ đủ 1 batch (sẽ lost nếu cách nhau >1 poll).
- Warren-vault pipeline build pattern (orchestrator + telegram intake + cron no_agent): `references/warren-pipeline-build-pattern.md`.
- E2E recipe + file map + exit codes + liteparse path fix + OCR covers-drop fix: `references/weekly-revenue-pipeline-e2e.md`.
- **Liteparse CLI BREAKS trên MSYS `/c/` path (2026-07-24, E2E ảnh thật).** Orchestrator gọi parser qua `subprocess` với path `/c/Users/...` (MSYS từ terminal) → parser truyền xuống liteparse CLI → liteparse nhận `\c\Users\...` → OCR FAIL dù file tồn tại. Symptom: chạy parser trực tiếp (path `C:\`) thì OCR đọc được; gọi qua orchestrator (path `/c/`) thì OCR FAIL. FIX: orchestrator truyền Windows path thuần `C:\Users\...` (hoặc parser convert `Path` sang `os.fspath` chuẩn Windows trước gọi liteparse). Khi debug OCR FAIL → CHECK PATH TRƯỚC kết luận "ảnh lỗi".
- **OCR drop cột giữa (covers) trên layout BI (2026-07-24).** `_primary_metric_row` phải lấy dòng value NGAY TRÊN dòng label "NET REVENUE", KHÔNG lấy dòng cuối trước label (dễ trúng header/date row → số rác). Ảnh thật LU3: covers (926) nằm giữa net_rev và avg → OCR bỏ sót → covers bị gán = avg (262430) → verify gate bắt SUM mismatch (stores 532515 != ALL 2583). Fix: `lines = [l for l in before.splitlines() if l.strip()]; value_line = lines[-1]`. Override JSON handler PHẢI accept `covers` + `avg` (không chỉ net_rev/tickets/ytd_rev) — khi OCR drop covers, Warren confirm số → override thiếu covers → verify vẫn fail.
- **dry mode PHẢI skip dashboard rebuild (không chỉ parser write).** `--dry` của parser chỉ skip append SSOT; `gen_revenue_dashboard.py` chạy riêng vẫn rebuild dashboard từ block giả. Orchestrator skip dashboard step khi `args.test or args.dry`. Biến git checkout revert dashboard nếu quên.
- **Test mode PHẢI 100% SIDE-EFFECT-FREE (mở rộng từ '--dry', 2026-07-24 revenue session).** Orchestrator `--test` KHÔNG được: (a) gửi Telegram thật (`--no-tg` mặc định khi test), (b) thử `git commit`/`git push` (`--no-git` mặc định khi test), (c) in log 'SSOT updated' khi thực tế đang `--dry`. Symptom session này: chạy `--test` → `[tg] OK` (spam Bố) + `[git] FAIL` (thử commit rác) + `[parse] OK — SSOT updated` (misleading, thực tế --dry không ghi). Fix: `--test` implies `--no-tg --no-git`; log ghi 'SSOT (dry, NOT written)'. Verify: chạy `--test` xong → `git status` phải sạch + Bố KHÔNG nhận tin + log không ghi 'updated'.
- **Session bị interrupt giữa lúc sửa → code hỏng → PHẢI py_compile TRƯỚC claim xong.** Session này: sửa indent orchestrator bị ngắt (Bố bảo 'tiếp tục' ở session khác) → file còn IndentationError dòng 129 → Bố 'không thấy pipeline' vì chạy là crash. Fix: trước mọi báo 'done' / trước session-end → `python3 -c "import py_compile; py_compile.compile(r'path', doraise=True)"` cho MỌI .py vừa sửa. Compile OK ≠ chạy OK, NHƯNG compile FAIL = chắc chắn hỏng → không được claim xong.
- **Artifact visibility với non-IT user (Warren).** File build xong mà Bố 'không thấy' thường do: (1) nằm trong dotfolder (`vault/.scripts/`) → Obsidian auto-ẩn (SOUL §5.2), (2) chưa `git commit` → GitHub không có. Fix: sau build → (a) scoped `git add` + commit, (b) tell Bố EXACT path + note 'nằm .scripts (ẩn Obsidian)'. Nếu Bố cần thấy trên Obsidian → copy/symlink ra non-dotfolder. Đừng để Bố tự mò.

## Pitfalls (thêm, 2026-07-25 cron verifier-audit session)
- **Silent-failure class (cùng 1 bug-family, bắt qua reviewer-node):** script nuốt exception → báo cáo/hành động SAI một cách câm lặng. 2 ví dụ thật:
  - `quota.py` (job `d235537ac561`, Model Router Daily Report): `load_state()` nuốt corruption rồi **auto-reset về 0** → báo "0% Pro" sai sự thật, KHÔNG exit ≠ 0. Fix: fail ≠ 0 khi state corrupt, KHÔNG auto-reset.
  - `col_telegram_intake.py` (job `16d81e801a39`): `_token()`/`_get_updates()` nuốt MỌI exception → return None/[]. Token hết hạn/mạng chết = **chết câm vĩnh viễn, không alert**. Fix: catch riêng → fail N lần → heartbeat alert / exit ≠ 0.
  - Đừng nhầm: "có `except`" ≠ "có verifier". `except` nuốt lỗi = **NGƯỢC verifier**.
- **Over-credit intake job:** verify thật ở tầng approve/pipeline (vd `col_queue_handler.approve_col()` read-back độc lập, `run_weekly_revenue_pipeline` 3-layer). Gán nhầm cho job intake = blind spot. Luôn check script intake trực tiếp.
- **LLM cron thiếu gate CẢ 2 tầng:** job `d235537ac561` là LLM cron, prompt chỉ "run + send", không có bước check → thiếu verifier ở prompt VÀ script. Audit LLM cron = đọc cả prompt lẫn script.
- **Reviewer-node bắt blind spot thực tế:** con tự mãn "chỉ 1 gap" → critic đọc script trực tiếp, bắt thêm 1 gap + 2 over-claim. Audit verifier = class task BẮT BUỘC qua A10.
- Worked example + grep recipe + critic transcript: `references/cron-verifier-audit-2026-07-25.md`.

## Pitfalls (thêm, 2026-07-29 COL SQL-fallback session)

### Gate 8 — SQL SSOT FALLBACK khi verify fail vì thiếu data từ parser (Warren directive)
> Warren: "nếu dữ liệu bố gửi thiếu, thì bước kế tiếp phải check SQL, hoặc đối chiếu với SQL vì đó là SSOT của doanh thu, cover, và AC"

Khi verify gate (read-back GSheet) phát hiện row NOT found cho 1 entity:
- ❌ SAI: Báo FAIL + để user retry. Entity bị skip vì parser regex thiếu 1 field (vd revenue không có format `"LU5: N,N"` trong brain dump) trong khi SQL SSOT CÓ data.
- ✅ ĐÚNG: Query SQL SSOT ngay tại verify step → nếu SQL có data → compute + append → re-verify → PASS. Chỉ FAIL nếu SQL cũng không có.

**Pattern áp dụng cho MỌI pipeline có SQL SSOT:**
1. Read-back verify fail → parse entity bị missing
2. Kiểm tra entity có đủ data thành phần từ parser không (vd: hours có nhưng revenue thiếu)
3. Nếu CÓ → query SQL SSOT cho data thiếu
4. Nếu SQL trả data → merge với parser data → append/update target
5. Re-verify → PASS hoặc FAIL thật

**Pitfall:** `parse_brain_dump()` là regex-based (KHÔNG phải LLM) — nếu text không có revenue đúng format → `missing_revenue` flag → store bị skip khi append. SQL fallback phải biết parse kết quả parser để lấy `hours_dict` còn thiếu.

**Pitfall:** Verify revenue mismatch (khác `row NOT found`) → KHÔNG dùng SQL fallback — đó là class bug khác (data conflict, cần human confirm).

### Gate 9 — HIDDEN CODE PATH: verify ALL callers after deploying a verifier fix
Khi deploy fix cho 1 verifier function, kiểm tra TẤT CẢ code path gọi function đó — không chỉ path hiển nhiên nhất.

- `col_queue_handler.approve_col()` được gọi bởi 2 path: `col_telegram_intake.py` (Telegram polling) VÀ `review_response_handler.py:360` (review queue agent cron).
- Nếu chỉ test 1 path → path kia vẫn dùng code cũ → user thấy lỗi cũ → nghĩ fix chưa deploy.
- Luôn `grep -rn "function_name" vault/.scripts/` sau khi deploy để confirm tất cả caller đều resolve đến module đã update.
