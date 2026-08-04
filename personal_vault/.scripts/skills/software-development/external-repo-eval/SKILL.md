---
name: external-repo-eval
description: "Đánh giá 1 repo/tool external có port được vào Hermes/warren-profile hay không, khi Warren bảo 'explore cái này' / 'steal cho existing'. Quyết định install-code vs steal-methodology + adapt cho free model. Class-level: áp dụng mọi lần Bố trỏ vào repo agent/tools ngoài."
version: 1.1.0
trigger: Warren trỏ link GitHub/repo external và hỏi 'cài/steal cho Hermes được không', 'dùng cho existing skill được không', 'explore cái này giúp bố'.
---

# /external-repo-eval — Cross-Runtime Repo Portability Assessment

> Khi Bố trỏ 1 repo external (vd: 1k★ deep-research harness) và hỏi "steal/cài cho Hermes",
> chạy quy trình này TRƯỚC khi hứa bất cứ gì. Sai lầm phổ biến: cố copy-paste code của
> repo chạy trên runtime khác → dead code. Đúng: bóc TINH THẦN, làm lại bằng tool Hermes.

## Quy trình 3 bước (BẮT BUỘC)

### B0 — KHÔNG dừng ở README (HARD RULE — học 2026-07-25)
Khi Bố bảo "explore / đánh giá repo này" → **BẮT BUỘC deep-dive TỪNG skill/file** của repo, KHÔNG dừng ở README/top-level.
- Sai lầm 2026-07-25: con đọc README → kết luận "95% overlap, không có gì thêm, KHÔNG ghi vào skill" → Bố vả: *"con hiểu lầm rồi, bố MUỐN con deep dive vào từng lệnh trong github đó, explore từng cái, song rồi advise bố"*. Dừng ở README = verdict sai + bỏ sót technique transferable.
- **Quy trình đúng:** (1) fetch raw `SKILL.md` THẬT của TỪNG skill từ repo (URL `.../skills/<dir>/<name>/SKILL.md` via web_extract/curl); (2) đọc kỹ, trích TECHNIQUE/WORKFLOW cụ thể (không chỉ mô tả); (3) so với vault stack → verdict **absorb vào skill nào** (dedup, KHÔNG tạo mới trừ khi phình) hoặc **SKIP + lý do**; (4) **ADVISE Bố** — deliverable là advise, KHÔNG tự quyết định adopt/skip.
- Repo lớn (vd mattpocock/skills ~22 skills) → spawn **parallel subagents** (1 nhóm/nhiều skill), mỗi con fetch+so-sánh, trả structured report tiếng Việt; orchestrator tổng hợp + advise.
- **Homogeneous bundle shortcut (học 2026-07-26, hermes-field-kit):** Khi repo chứa N skill CÙNG 1 layout (vd Field Kit: 4 skill audit đều có đúng 10 file `SKILL.md`+`README.md`+`references/{protocol,safety,report-contract}.md`+`examples/`+`scripts/validate_bundle.py`+`tests/`), ĐỪNG đọc mù 10×N file. Quy trình: (1) `find <dir> -type f | sort` xác nhận layout đồng nhất; (2) đọc TOÀN BỘ 10 file của **1 skill mẫu** → học kiến trúc dùng chung (validator pattern, test harness, safety doctrine, shared bundle contract); (3) với N−1 skill còn lại chỉ đọc file **KHÁC BIỆT** (`SKILL.md`, `examples/example-report.md`, `references/{protocol,report-contract}.md`, `tests/cases.json`) — bỏ qua file boilerplate lặp lại (validate_bundle.py, test_contracts.py, safety.md thường chỉ khác tên skill). Batch tất cả read trong 1 turn (independent calls). Tiết kiệm ~60% token, không mất fidelity. Report structure: 1 mục "Shared architecture" chung + 1 mục/skill cho phần khác biệt.
- Kết quả đúng của session 2026-07-25: 12 technique đáng hút vào 8 skill có sẵn (wayfinder Decision-Map, to-tickets expand-contract, triage state-machine, diagnosing-bugs falsifiable-hypotheses, tdd tautological-check, domain-modeling 3-condition-ADR, improve-codebase-architecture deletion-test, ask-matt context-hygiene...). Xem `references/mattpocock-skills-steal-map.md` (đã có) cho steal-map mẫu.

### B1 — Runtime-lock check (quyết định sống/chết)
Đọc README/Requirements của repo, tìm:
- Runtime bắt buộc: `Claude Code`, `Cursor`, `Codex`, app trả tiền, CLI cụ thể?
- Tool riêng: `Skill` tool của Claude Code, subagent roster, allowlist `[Read,Edit]`, SQLite riêng?
- Model hardcode: Sonnet/Opus/Haiku (trả tiền)?
- **MCP protocol:** repo có cung cấp MCP server không? (check `mcp`, `modelcontextprotocol` trong README/pyproject.toml — Hermes support MCP native qua `hermes mcp add`, không cần `--agent hermes`.)

→ Nếu CÓ runtime lock (Claude Code skill, Cursor extension, v.v.): **"install/steal code" = ❌**. Copy vào Hermes = vô dụng (khác ngôn ngữ lệnh, như code Android bỏ vào iPhone).
→ Nếu KHÔNG (pure Python lib, CLI chuẩn, model-agnostic): có thể cài thật (pip/clone) rồi wrap.
→ Nếu là **MCP server** (dù có runtime lock với agent khác, miễn nó nói MCP protocol): Hermes vẫn xài được qua `hermes mcp add`. Đây là ngoại lệ quan trọng — không vội kết luận "không cài được".
**⚠️ PRE-DRAFT GATE (học 2026-07-22, áp强制 trước B2):** TRƯỚC khi draft bất cứ đề xuất steal nào (absorb vs create vs reject), BẮT BUỘC re-read pitfall **`🔴 P1 — "Steal = new skill" bias`** ở cuối SKILL.md này. Session 2026-07-22: con SKIP bước này → đề xuất A-D "absorb tất cả vào skill có sẵn" → vi phạm chính progressive-disclosure của repo + tăng context-load → critic (reviewer-node) forced REJECT, mất 1 vòng. Rule: P1 đã dạy "tách riêng nếu concern KHÁC, CREATE nếu phình skill". Luôn consult P1 TRƯỚC draft, không đợi critic bắt.

### B2 — Decision rule
| Trường hợp | Hành động | Deliverable |
|-----------|-----------|-------------|
| Runtime-locked app (như hyperresearch) | **Steal methodology** ✅ | Skill MỚI viết lại bằng tool Hermes (mcp_smart_search, delegate_task, verify-parser-output, execute_code) |
| **MCP Server** (nói MCP protocol, `pip install` được, Hermes-native) | **`hermes mcp add` + test** ✅ | Chạy `hermes mcp add <name> --command <cmd>`, verify `hermes mcp list` + `hermes mcp test`. Không cần wrapper skill — tools auto-discover. Kèm cài dependency (Playwright Chromium, model file,...). |
| Pure lib / CLI chuẩn | **Install + wrap** ✅ | Clone/pip, viết thin dispatcher skill (xem `using-agent-skills` §Multi-Profile) |
| Trùng skill Warren có sẵn | **Dedup** ✅ | Absorb mechanics vào skill cũ, KHÔNG add parallel |
| Cần trust-audit repo/tool | **Reference oss-tool-trust-audit** ✅ | Dùng B4 verdict enum + Skillspector (`skill-security-audit`); KHÔNG tạo skill trùng tên |

### B3 — Adapt cho free model (nếu source giả định model mạnh)
- `delegate_task` kế thừa model parent → **chunk ≤3 concurrent** (giới hạn hệ thống; NEVER 17-at-once như bản gốc chạy Sonnet).
- Delay nhỏ giữa search waves → tránh rate-limit ban trên hy3:free / Nemotron free.
- **Auto-fallback:** gặp 429/ban → drop xuống pipeline gọn hơn + báo Bố. KHÔNG cố chạy tới hỏng.
- **Honest tradeoff:** nói thẳng Bố — free model yếu → báo cáo nông hơn benchmark gốc. Bù bằng kỷ luật cite-check + critic (SOUL §5), không cậy model khỏe.

### B4 — Trust verdict (reference oss-tool-trust-audit, học 2026-07-27)
Khi eval 1 tool/repo external mà cần verdict "có an toàn không / có cài không", reference methodology của skill `oss-tool-trust-audit` (field-kit) làm upstream standard — KHÔNG tạo skill trùng tên (warren-profile đã có `skill-security-audit` + `external-repo-eval` làm equivalent).
- 5-verdict enum: `USE` / `USE WITH CONTROLS` / `ISOLATE AND TEST` / `DO NOT USE` / `INSUFFICIENT EVIDENCE`.
- 11-heading Report Contract: OSS Tool Trust Audit / Verdict / Subject and Version / Legitimacy / Provenance and Maintainers / Telemetry and Network / Dangerous Capabilities / Dependencies and Supply Chain / Claim Verification / Adoption Fit / Unknowns / Recommended Controls.
- 7-step procedure của nó (identify → inspect release/provenance → inspect critical code → inspect deps → verify claims → assess runtime boundaries → adoption fit) map trực tiếp vào B1–B3 ở trên + P5.
- Rule: borrow verdict enum + report-contract headings vào bài eval (như phần này) để faithful với standard; KHÔNG duplicate toàn bộ skill.

### B5 — Whole-catalog evaluation (skill ecosystem, không phải single tool)

Khi repo external chứa **cả bộ sưu tập skills** (vd OMH 92 skills, mattpocock/skills 22 skills) — đánh giá khác với single tool. Áp dụng quy trình này:

#### B5.1 — Catalog-source shortcut (học 2026-07-29, OMH analysis)
Nếu repo **GENERATE skills từ catalog source** (Python dataclass, YAML manifest, JSON definitions) — **đừng đọc N file SKILL.md riêng**. Đọc catalog source TRƯỚC:
- Tìm file: `catalog.py`, `catalog_definitions.py`, `catalog_types.py`, hoặc tương đương (`src/skills/catalog.py`, `lib/catalog.rb`, `definitions.json`).
- Đọc catalog code → biết **tổng thể skill list + mô tả + category** trong 1 pass, thay vì N pass.
- Sau đó chỉ đọc chi tiết **sample skills** (3-7 skill đại diện cho các category khác nhau) để hiểu format/template.
- Tiết kiệm 70-90% token so với đọc từng skill.

Dấu hiệu nhận biết repo có catalog source:
- File `catalog.py` / `catalog_definitions.py` / `catalog_types.py` trong `src/skills/` hoặc tương tự.
- File `render.py`, `generate.py`, `build.py` — script render SKILL.md từ data.
- File `definitions.json` / `skills.yaml` / `manifest.json` chứa tất cả skill metadata.
- Các file SKILL.md có cấu trúc y hệt nhau (template) → gợi ý generated.

#### B5.2 — Three-way categorization deliverable
Kết quả so sánh toàn bộ catalog external vs local inventory phải trả về 3 bucket rõ ràng:

| Bucket | Định nghĩa | Hành động |
|--------|-----------|-----------|
| **(1) Overlap / khác tầng** | Tên giống Warren nhưng purpose khác hẳn (vd OMH code-review = routing meta-skill, Warren code-review-and-quality = actual multi-axis review) | Ghi rõ "name overlap only — different abstraction layer" |
| **(2) New / bổ ích** | Concept Warren CHƯA có, adapt được | Liệt kê + mức priority (HIGH/MOD/LOW) + cách adapt |
| **(3) Engineering-only / irrelevant** | Chỉ áp cho software engineer, không liên quan F&B ops / stock / personal | Ghi lý do skip + count |

#### B5.3 — "Steal methodology, not skill files" (học 2026-07-29)
Kết luận của whole-catalog evaluation KHÔNG phải "adopt 3 skills này" (vì external skill phụ thuộc runtime/infra/CLI của họ). Mà là:
- **"Steal N patterns"** — liệt kê từng pattern cụ thể (vd: instinct-ledger's structured confidence-scored ledger, failure-signal-audit's swallowed-error hunting).
- **Prioritized** — HIGH/MOD/LOW, mỗi pattern kèm 1 câu "why needed".
- **Adapt-for-free-model note** — pattern này có cần model mạnh không? Chạy được trên DeepSeek free?
- **Hành động:** mỗi pattern = 1 lần patch vào skill Warren có sẵn, hoặc tạo skill mới nếu concern khác.
- Không recommend copy SKILL.md của họ vào warren-profile (sai runtime, sai domain, sai model).

#### B5.4 — Naming convention for analysis output
Lưu report vào:
- `vault/_inbox/research/<project>-vs-warren-analysis.md`
- Frontmatter: `type: external-ecosystem-eval`, `source: <repo-url>`, `verdict: steal-methodology | skip-full | partial-adopt`.

## Giải thích cho dân non-IT (template VN)
> "Thưa Bố, cái này là app iPhone (chạy trên nền của họ), nhà mình xài Android (Hermes) nên
> không cài trực tiếp được. Nhưng ý tưởng hay của họ (cách làm X) con bóc ra, làm bản Hermes
> 0₫, chạy trên model free của Bố. Không cần trả tiền, không cần app lạ."

## Vault store (đừng dùng storage của repo gốc)
- Output bài research/test → `vault/_inbox/research/<slug>.md` (hoặc `_growth/` theo ý Bố), KHÔNG dùng SQLite/καθε riêng của repo.
- Skill mới viết vào `warren-profile/skills/<name>/` (custom tree, editable).

### Deliverable shape khi steal methodology
Build như 1 skill mới theo **Warren Ops Workflow** (`using-agent-skills`): interview → spec → plan → incremental per-slice (Implement → Verify → Review+Simplify) → backup vault. Xem `references/hyperresearch-case.md` cho worked example (build skill mới từ methodology), `references/hound-mcp-case.md` cho worked example (MCP server install), và `references/auto-company-case.md` cho worked example (steal methodology → absorb vào skill CÓ SẴN, không tạo skill mới — 3 pattern patch vào safenet + SOUL + ops-case-lifecycle).

**Warren approval-gate (CONFIRMED 2026-07-22):** Warren REQUIRES the SPEC + PLAN be **presented inline for his explicit "ok/approved" BEFORE any `skill_manage(action='create'/'patch')`**. His exact words this session: *"dùng using-agent-skills nha con, rồi gửi bố spec-driven-development và planning-and-task-breakdown"* + *"incremental-implementation và Verification"*. Practical shape that worked: (1) write SPEC inline (adapted for skill-doc: drop Tech Stack/Commands/Code Style/Testing; keep Objective / Files-to-change / Boundaries / Success Criteria), (2) write PLAN = micro-tasks ≤5min, vertical slices, acceptance+verify per task, (3) present both → wait Warren "ok", (4) ONLY THEN implement slice-by-slice with per-slice verify (skill_view / terminal grep / read_file — NOT search_files which false-negatives on skills/ dir), (5) backup to `vault/_archives/skills/` + emit `📦 ARCHIVE:`. Skipping the spec/plan gate = re-work.

## Pitfalls
- **Runtime theater:** đọc Requirements kỹ. Nhiều repo ghi "Python 3.11+" nhưng thực tế cần Claude Code → vẫn lock.
- **Model FOMO:** đừng hứa chất lượng benchmark gốc trên free model. Bố thích honest (SOUL §5 Pushback).
- **Duplicate skill:** nếu Warren đã có skill tương tự (vd `research`, `capture`), absorb chứ đừng tạo song song → vi phạm simplify/SSOT.
- **Env-dependent failures:** lỗi thiếu binary/credential KHÔNG phải lý do để bỏ repo — đó là setup, sửa riêng.
- **"Steal = new skill" bias (CẦN SỬA — học 2026-07-22):** KHÔNG auto-absorb, cũng KHÔNG auto-tạo. Quy tắc:
  - **Absorb** vào skill hiện tại CHỈ KHI methodology bị steal **CÙNG 1 concern** (vd auto-company: 3 pattern → safenet/SOUL/ops-case-lifecycle đều là "ops governance").
  - **CREATE skill riêng** khi methodology là **concern KHÁC** với mọi skill có sẵn (vd `writing-great-skills` = design-quality, KHÁC với `hermes-agent-skill-authoring` = mechanical packaging → tách riêng, `disable-model-invocation: true`). Hoặc khi absorb sẽ **phình skill** → tăng context-load trên free model (hy3:free) → rủi ro truncation.
  - **Test:** nếu repo gốc tự tách 1 concern thành standalone reference skill → mirror cấu trúc đó, ĐỪNG collapse. Repo's own organization là canonical example của principles nó dạy.
- **🔴 P6 — CROSS-CHECK existing warren-profile inventory TRƯỚC adopt/patch verdict (học 2026-07-26, hermes-field-kit):** Khi kết luận "cài skill X vào profile" hoặc "patch Y vào using-agent-skills", BẮT BUỘC liệt kê skill ĐÃ CÓ trong `warren-profile/skills/` TRƯỚC. Session 2026-07-26: con recommend adopt `interview-me` (từ field-kit) + patch `incremental-implementation`/`writing-great-skills`/`verify-parser-output` vào `using-agent-skills` → Bố bắt: *"interview-me bố cũng có (nằm trong using-agent-skills); còn 4 lệnh là code hay prompt? có ghi/patch vào command nào trong using-agent-skill được ko?"* — tức toàn bộ cái con đề xuất ĐÃ CÓ sẵn. Blind spot: con nhìn repo ngoài mà quên tra kho nội bộ. Rule: (a) mọi adopt/skip/patch verdict → chạy `search_files`/`find` danh sách skill profile trước; (b) nếu repo ngoài có skill trùng capability đã có → KHÔNG cài (dedup, chỉ borrow rule khác biệt); (c) nếu định patch 1 skill vào `using-agent-skills`, kiểm tra skill đó ĐÃ nằm trong router chưa (tránh double-list). Tiết kiệm 1 vòng reject của Bố.
- **🔴 P7 — PROFILES MAY SHARE A SKILLS TREE (học 2026-07-26, hermes-field-kit adopt):** Khi patch 1 skill (vd `using-agent-skills`) trong `warren-profile`, verify xem `stock-profile` (và các profile khác) có CÙNG file không — dùng `stat -c '%y' <file>` trên cả 2 path. Session 2026-07-26: patch `using-agent-skills` trong warren-profile → `stock-profile` tự động có THAY ĐỔI IDENTICAL (timestamp trùng khớp exact `09:13:33.884`). Nghĩa là 2 profile trỏ chung 1 skills tree (symlink / shared dir) → patch 1 chỗ = cả 2 có. Rule: (a) TRƯỚC khi patch thủ công nhiều profile, chạy `stat` để biết có shared tree không; (b) nếu shared → chỉ patch 1 lần (không lặp); (c) nếu độc lập → patch từng profile riêng. Tiết kiệm công + tránh drift giữa các profile. (Lưu ý: đây là property của setup máy Warren, không phải lỗi — verify bằng `stat` mỗi lần vì có thể tách profile sau này.)
- **Repo's structure is canonical (học 2026-07-22):** Coi cấu trúc skill-split của repo gốc là bài thi mẫu. Repo tách `writing-great-skills` thành reference riêng → mình cũng tách riêng, ĐỪNG nhồi vào skill khác (sẽ mix 2 concern + bloat context). Over-absorb vi phạm chính progressive-disclosure của repo.
- **Đừng miss high-ROI steals (học 2026-07-22):** Khi research repo, QUÉT TOÀN BỘ skill list — đừng chỉ map 4 failure-mode nổi bật. Steal có ROI cao nhất thường là: (a) **router section** (trong `using-agent-skills` — mục "Ask Hermes — Warren Router") khi user-invoked skills quá tải cognitive load [đã gộp từ `ask-hermes` cũ 2026-07-24]; (b) **architectural-audit routine** (`improve-codebase-architecture` deletion-test + scope-before-scan → áp parser pipeline); (c) **root-cause debugging** (`diagnosing-bugs`). → Steal-map mẫu: `references/mattpocock-skills-steal-map.md`.
- **🔴 P8 — GitHub Contents API `size:0` KHÔNG PHẢI folder rỗng (học 2026-07-27, interview-me field-kit):** Khi list repo via `https://api.github.com/repos/<owner>/<repo>/contents/<path>`, API trả `"size": 0` cho MỌI **directory (tree object)** — bất kể folder có chứa file hay không. Session 2026-07-27: con đọc `"size":0` của `skills/interview-me/{examples,references,scripts,tests}` → KẾT LUẬN "4 folder rỗng, script/tests không tồn tại" → SAI. Thực tế folder CÓ file thật (`validate_bundle.py` 6294B, `tests/*.py`, `references/*.md`). Hậu quả: con báo "pure markdown, safety=0, README over-claim" → bị critic (reviewer-node) bắt FAIL. **Quy tắc đúng:** để biết 1 subfolder có file hay không, BẮT BUỘC `curl` tiếp URL con của TỪNG subfolder (`.../contents/skills/<skill>/scripts`, `/tests`, `/references`, `/examples`) và đọc mảng `name/size/type` trả về — KHÔNG kết luận "rỗng" từ `size:0` của parent. Áp mọi lần eval repo external: luôn list sâu từng cấp, đừng trust size của directory.

### 🔴 P5 — Verify claims EMPIRICALLY, đừng tin doc (học từ deep-review x-analytics-import 2026-07-26)
Khi eval 1 skill/repo external mà nó **tự tuyên bố** ("code is real/runnable not a stub", "private-by-default", "no network side effects", "idempotent", "tests all pass") → BẮT BUỘC verify bằng chứng cứ, KHÔNG paraphrase doc:
- **"Real, not a stub"** → CHẠY test suite thật (`python -m unittest discover -s <skill>/tests -v`). Report pass/fail count + thời gian thật. VD 21/21 pass trong 0.232s = bằng chứng; "code trông đầy đủ" = phỏng đoán.
  - **⚠️ False-FAIL từ `__pycache__` (học 2026-07-26):** Nhiều bundle ship `validate_bundle.py` có bước quét 'no generated artifacts'. Lần chạy test đầu PASS; nhưng validator/test lần 2 báo FAIL `generated artifact present: scripts\__pycache__` hoặc `'__pycache__' unexpectedly found` — false positive tự gây ra (chính lần chạy test tạo cache, rồi bị bắt lại). FIX: chạy `python -B -m unittest discover -s <bundle>/tests` (`-B`=no bytecode), hoặc dọn trước `find <repo> -name __pycache__ -type d -exec rm -rf {} +`. Khi advise Bố: report 'tests PASS', ghi rõ FAIL kia là artifact tự-sinh KHÔNG phải defect repo — đừng kết luận 'tests failing'. Đây KHÔNG phải env failure, là property bền của Python cache × bundle tự-quét. Worked example: hermes-field-kit 3 skill (validator PASS + 10/26/10 tests OK sau khi thêm `-B`).
- **"Private / no network / no side effects"** → grep import list cho `requests/urllib/httpx/socket/subprocess/git`; xác nhận mọi file-write đều nằm dưới `--output-dir`. Nếu có "leak guard"/"redaction" → đọc code THẬT của guard (nó là token-blocklist hay content-scan?) và nói rõ giới hạn.
- **"Idempotent / dedup"** → tìm cơ chế thật (vd SHA-256 manifest ledger) + test chứng minh (`already_imported`).
- **Đối chiếu doc vs code:** flag mọi chỗ doc hứa nhưng code KHÔNG enforce (vd doc bảo "output ngoài repo" nhưng default `--output-dir=cwd()/...` có thể rơi vào repo → red flag "doc-level rule, not code-enforced"). Đây là loại red flag giá trị nhất cho Bố.
- Deliverable: mỗi claim lớn phải kèm 1 dòng bằng chứng ("verified: ran suite 21/21 pass" / "no network imports found" / "leak guard = token blocklist tại line X, không scan nội dung"). KHÔNG bao giờ trả verdict "code is real" chỉ từ đọc.
- Áp cả khi Bố chỉ bảo "deep-research skill này" (KHÔNG hỏi cài) — deliverable vẫn là advise, nhưng phải là advise CÓ bằng chứng chạy, không chỉ đọc-và-tóm-tắt.
- **Test FAIL ≠ skill hỏng (học 2026-07-26, hermes-field-kit 4 audit skills):** Khi chạy test suite mà thấy FAIL, ĐÀO nguyên nhân (`... 2>&1 | grep -A20 "FAIL:"` xem traceback) TRƯỚC khi báo "tests fail". Gotcha thật: cả 4 skill `validate_bundle.py` → PASS nhưng mỗi bộ unittest báo 1 FAIL — nguyên nhân là `test_no_private_paths_secrets_or_generated_artifacts` tự tạo `__pycache__/` khi Python chạy nó, rồi chính nó flag `__pycache__` là "generated artifact". Đây là **harness tự-nhiễm (self-poison false-positive)**, KHÔNG phải defect của skill. Report 2 fact riêng: "validator PASS" + "1 test fail do harness artifact, không phải lỗi skill". Class rule: phân biệt (a) fail phản ánh subject thật hỏng vs (b) fail do chính test tạo ra side-effect rồi tự bắt (thường: __pycache__, temp files, .pyc, mtime, cwd-dependent glob). Chỉ (a) mới là red flag cho Bố.

### 🔴 P1 — Đừng ghi file vào thư mục skill (học từ deep-research test 2026-07-20)
- Sai: `skills/<name>/vault/_inbox/...` (con từng ghi nhầm vào đây khi test).
- Đúng: `C:\Users\khoans\Documents\Warren_OS_Local\vault\_inbox\research\<slug>\...`
- Vault thật của Bố KHÔNG nằm trong `AppData/.../skills/`. Luôn ghi output vào `Documents/Warren_OS_Local/vault/`.

### 🔴 P2 — MCP server cần verify tools hiện trên Hermes, không chỉ pip install
- Sau `pip install` + `hermes mcp add <name> --command <cmd>`, BẮT BUỘC chạy `hermes mcp test <name>` + `hermes mcp list` để confirm tools hiện.
- Một số MCP server cần thêm binary (Playwright Chromium, v.v.) — đừng bỏ qua bước cài dependency.
- `hermes mcp add` có interactive prompt (hỏi enable tools) — dùng `echo Y | hermes mcp add ...` để bypass khi chạy non-interactive.
- Nếu Hermes Desktop báo lỗi MCP connection, kiểm tra: (a) command có trong PATH không, (b) server có startup <1s không (MCP handshake timeout), (c) `hound --version` standalone OK trước.
- MCP tools xuất hiện sau `/reload-mcp` hoặc session mới — không panic nếu chưa thấy ngay.
- **Multi-profile:** MCP server cài 1 lần (pip global) nhưng cần `hermes mcp add` cho TỪNG profile riêng: `echo Y | hermes --profile <profile-name> mcp add <name> --command <cmd>`. List profile names: `hermes profile list`.

### 🔴 P3 — Bố có thể yêu cầu full workflow sau eval decision
- Sau khi quyết định "install MCP server" hoặc "steal methodology", Bố có thể yêu cầu apply toàn bộ `using-agent-skills` workflow (constitution → spec → plan → incremental-implementation) — đừng chỉ pip xong rồi báo done.
- Luôn hỏi Bố: "Bố muốn con cài luôn hay làm theo workflow?" trừ khi Bố đã nói rõ "apply toàn bộ".
- Constitution gate (step 0o) KHÔNG được skip vì lý do "task đơn giản" — hỏi Bố trước, đừng tự quyết định. (Lesson 2026-07-21: con từng skip constitution cho Hound install vì nghĩ "chỉ cài tool" → Bố bắt quay lại làm đúng.)
- Subagent chạy context/terminal riêng → resolve `vault/...` thành `C:\Users\khoans\vault\...` (SAI, thiếu `Documents/Warren_OS_Local/`).
- Triệu chứng: subagent báo `File not found: C:\Users\khoans\vault\_inbox\...`.
- **FIX (BẮT BUỘC cho mọi delegate_task truyền path):** dùng **absolute path đầy đủ**
  `C:\Users\khoans\Documents\Warren_OS_Local\vault\...` trong context. KHÔNG dùng relative `vault/...`.
- `execute_code` bị block trong cron mode → dùng `terminal` + `python3` thay thế cho compute nhẹ.
- Verify trước mỗi write/dispatch: path bắt đầu `C:\\Users\\khoans\\Documents\\Warren_OS_Local\\vault\\` (không phải `AppData/.../skills/` cũng không phải `C:\\Users\\khoans\\vault\\`).
- **🔴 P4 — Steal the repo's self-eval rubric too (học 2026-07-23).** Khi ABSORB methodology vào skill CÓ SẴN, đừng chỉ lấy quy trình — cũng lift artifact tự-kiểm của repo (vd: `petergyang/no-ai-slop` có `eval.md` = checklist PASS/FAIL chạy trên output của chính nó). Biến nó thành 1 bước **self-check gate** cụ thể trong Process của skill đích (vd: `humanizer` absorbed eval.md thành Process step 5 — chạy checklist TRƯỚC khi trả output). Lý do: skill chỉ có hướng dẫn thì dễ drift; có rubric tự-soi → output tự-verify, không cần người đọc dò từng dòng. Tín hiệu nhận biết repo có rubric: file `eval.md` / `checks.md` / `quality.md` / section "Self-review" trong README. Worked example: `humanizer` (creative/) v2.5.1 + eval checklist từ no-ai-slop (vault commit 7a36bc2, 2026-07-23).
- **🔴 P9 — "Same name, different layer" trap (học 2026-07-29, OMH analysis):** Đừng kết luận "trùng → skip" khi 2 skill cùng tên. Có thể external skill ở tầng routing/meta (nói về cách classify request) còn Warren skill ở tầng execution (nói về câu lệnh thật). Trường hợp này verdict là **"tên trùng, khác tầng"** — không phải overlap cũng không phải new concept. Ghi rõ abstraction layer của mỗi skill. VD: OMH `code-review` = routing meta-skill, Warren `code-review-and-quality` = actual code review with findings-and-evidence pipeline. Cùng tên, khác layer.
- **🔴 P10 — Generated skills need catalog-source analysis (học 2026-07-29, OMH analysis):** Nếu repo dùng generator (catalog.py → SKILL.md), ĐỪNG đọc N file SKILL.md riêng (tốn token vô ích). Đọc catalog source trước — nó chứa mọi thông tin cần cho comparison. Dấu hiệu: file `catalog.py`, `render.py`, template pattern trong SKILL.md files. Homogeneous bundle shortcut (học 2026-07-26) chỉ đúng khi skill viết tay; skill generated luôn giống nhau về format — đọc source KHÔNG phải từng file.
- **🔴 P11 — Subagents find better patterns than main agent (học 2026-07-29, OMH eval):** Khi deep-dive repo lớn (92+ skills), B0 PHẢI dùng parallel subagents — chúng đọc TOÀN BỘ file, không bỏ sót như main agent chỉ đọc README+sample. Session này: con đề xuất 4 technique từ đọc README+samples → subagents tìm 4 pattern KHÁC TỐT HƠN (instinct-ledger, failure-signal-audit, decision-recall, workflow-learning) từ catalog 4430 dòng. Main agent blind spot = agent không đọc toàn bộ. Rule: với repo >50 files → B0 MANDATORY spawn subagents, không tự đọc. Kết quả subagent LÀ SỰ THẬT — nếu khác với main agent đọc, tin subagent.
- **🔴 P12 — `patch` replace thay vì insert trong bảng routing (học 2026-07-29, safenet patch):** Khi thêm dòng vào bảng routing của safenet dùng `patch`, old_string khớp dòng hiện có → bị REPLACE thay vì INSERT. Hậu quả: 2 lần mất dòng quan trọng ("Warren analysis/report" và "Major decision"). Fix: old_string PHẢI chứa dòng MỚI + dòng BÊN DƯỚI, new_string = dòng mới + dòng bên dưới — đảm bảo insert, không replace. Mẫu: `old_string="| Dòng sát trên | ... | If ... |"`, `new_string="| Dòng mới | ... | If ... |\n| Dòng sát trên | ... | If ... |"`. Hoặc dùng `write_file` ghi toàn bộ file khi bảng routing có nhiều dòng.
