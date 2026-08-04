---
name: using-agent-skills
description: Discovers and invokes agent skills. Use when starting a session or when you need to discover which skill applies to the current task. This is the meta-skill that governs how all other skills are discovered and invoked.
---

# Using Agent Skills

## Overview

Agent Skills is a collection of engineering workflow skills organized by development phase. Each skill encodes a specific process that senior engineers follow. This meta-skill helps you discover and apply the right skill for your current task.

---

## 🤔 Ask Hermes — Warren Router (Bố-facing)

> Bối rối giữa các skill? Đọc bảng này, chọn đúng phase, gõ tên skill. Không đoán — restate + confirm với Bố.

**Route rule:** Hỏi "Bố đang ở đâu — chưa rõ ý / có spec / đang build / đang verify?" → chọn phase → gõ skill tương ứng.

### Define-phase (chưa rõ muốn gì)
- **interview-me** — ask mơ hồ ("build X" thiếu who/why). Hỏi 1 câu/lần + GUESS. Warren: còn build CONTEXT.md glossary + ADR.
- **idea-refine** — đã rõ ý cơ bản, cần sinh biến thể/tìm hướng.
- **spec-driven-development** — có ý rõ → viết spec (6 vùng: objective/commands/structure/style/testing/boundaries).
- **planning-and-task-breakdown** — có spec → bẻ task có acceptance + verify, vertical slices.
- **generate-plan** — nhanh, tạo plan từ ý thô (lightweight alternative cho planning-and-task-breakdown).

### Build-phase
- **incremental-implementation** — implement slice-by-slice (Implement→Test→Verify→Commit). Có expand-contract cho wide-refactor.
- **test-driven-development** — test-first (red-green), test tại seam.
- **writing-great-skills** — reference khi viết/sửa skill (predictability, ladder, 6 failure modes).
- **improve-codebase-architecture** — audit parser/vault pipeline (scope-before-scan, deletion-test).

### Verify/Review-phase
- **verify-parser-output** — MANDATORY gate sau LLM parse/compute từ Excel/CSV/PDF. Independent recompute + cross-assert.
- **qa-gate** — QA execution gate — aggregate verify-parser + ab-test (+ battle-test + speckit-converge for qa-full) → PASS/FAIL trước reviewer-node. 🟢=qa-min, 🟡/🔴=qa-full. Auto-fire qua safenet §D.
- **code-review-and-quality** / **code-simplification** — 5-axis review + inline single-pass simplify (default, cheap, có L'Usine parser pitfalls).
- **simplify-code** — 4-altitude *parallel* cleanup (line→function→module→architecture) khi Bố muốn review sâu. Bố nói "dọn code/làm gọn/simplify/clean up" → default là `code-simplification`; cần deep review → gọi `simplify-code`.
- **debugging-and-error-recovery** / **diagnosing-bugs** — root-cause khi code bể.

### Meta/Ops
- **session-start** — bootstrap mỗi session (auto-load, nhưng gõ để re-run).
- **safenet** — pre-output adversarial gate (auto khi analysis).
- **qa-gate** — QA execution gate — aggregate test results → PASS/FAIL. Auto-fire qua safenet §D, trước reviewer-node.
- **reviewer-node** — independent critic (auto spawn theo safenet, sau qa-gate PASS).
- **compress-memory** — distill memory hàng tuần.
- **handoff** — compact session sang file cho agent khác.
- **explore** — ops-feasibility validation trước khi build.

### Hermes Doctor (VI) — wrapper tiếng Việt gọi 3 doctor từ hermes-field-kit
> Source: `asimons81/hermes-field-kit` (Apache-2.0, prompt-only, read-only, approval-gated). Đã copy vào `warren-profile/skills/`. Wrapper này (2026-07-26, Bố duyệt) chỉ map trigger TIẾNG VIỆT → skill đúng, KHÔNG thay đổi source gốc.
- **"cron chạy chưa / stack có khỏe không / sáng nay automation có chạy không"** → `hermes-stack-doctor` (health-check toàn bộ → GREEN/YELLOW/RED: cron/gateway/skills/profiles/cost).
- **"bot chết / Telegram không nhận tin / gateway lỗi / bị 409 conflict"** → `hermes-gateway-doctor` (chẩn đoán Telegram/Discord, tiền silent-death + polling conflict).
- **"dọn skill trùng / audit 200 skills / skill nào hỏng / skill nào cũ"** → `hermes-skill-audit` (tìm overlap/stale/broken-ref, check cron dependency TRƯỚC khi xóa).
- **"tool này có an toàn không / eval repo GitHub trước adopt"** → `oss-tool-trust-audit` (COMPLEMENT cho `deep-research-tool-fit`/`external-repo-eval`/`skill-security-audit`, không cài trùng, chỉ reference). Dùng khi Bố nhờ eval tool/skill ngoài.
- ⚠️ 3 doctor = **prompt/checklist**, KHÔNG có code chẩn đoán; chất lượng = chất lượng Con chạy. Chạy trên 200+ skills tốn token nhiều. Luôn load đúng skill theo trigger, đừng đoán.

---

## Skill Discovery

When a task arrives, identify the development phase and apply the corresponding skill:

```
Task arrives
    │
    ├── New project/feature/change needing governing principles first? ──→ speckit-constitution  (Spec-Kit: project constitution / "luật chơi")
    ├── Don't know what you want yet? ──────→ interview-me  (Warren override: also builds CONTEXT.md glossary + writes ADR per decision)
    ├── Have a rough concept, need variants? → idea-refine
    ├── New project/feature/change? ──→ spec-driven-development
    ├── Have a spec and need artifact completeness/quality check before planning? ──→ speckit-checklist  (Spec-Kit: checklist artifacts sau spec)
    ├── Have a spec, need tasks? ──────→ planning-and-task-breakdown
    ├── Implementing code? ────────────→ incremental-implementation
    │   ├── UI work? ─────────────────→ frontend-ui-engineering
    │   ├── API work? ────────────────→ api-and-interface-design
    │   ├── Need better context? ─────→ context-engineering
    │   ├── Need doc-verified code? ───→ source-driven-development
    │   └── Stakes high / unfamiliar code? ──→ doubt-driven-development
    ├── Writing/running tests? ────────→ test-driven-development
    │   └── Browser-based? ───────────→ browser-testing-with-devtools
    ├── Something broke? ──────────────→ debugging-and-error-recovery
    ├── Reviewing code? ───────────────→ code-review-and-quality
    │   ├── Too complex? ─────────────→ code-simplification
    │   ├── Security concerns? ───────→ security-and-hardening
    │   └── Performance concerns? ────→ performance-optimization
    ├── Committing/branching? ─────────→ git-workflow-and-versioning
    ├── CI/CD pipeline work? ──────────→ ci-cd-and-automation
    ├── Deprecating/migrating? ────────→ deprecation-and-migration
    ├── Writing docs/ADRs? ───────────→ documentation-and-adrs
    ├── Adding logs/metrics/alerts? ───→ observability-and-instrumentation
    ├── Need to stress-test? ──────────→ battle-test
    ├── Have built code and need to reconcile against spec/plan/tasks before final review? ──→ speckit-converge  (Spec-Kit: converge/đối chiếu code vs spec)
    ├── Need to A/B test? ─────────────→ ab-test
    ├── Deploying/launching? ─────────→ shipping-and-launch
    └── Ending session with work half-done? → handoff  (compact context into vault for next session/agent)
```

---

## 🧊 Interview & Freeze Gate (Warren's #1 Rule)

> **Why:** The #1 reason AI agents fail is starting work BEFORE fully understanding the prompt — silent assumptions → wrong output → hours wasted. 30 seconds freezing saves hours of untangling.

**HARD RULE — applies to ALL tasks, even "trivial" ones:**

Before ANY spec, plan, task breakdown, or implementation — if requirements are not 100% clear:

1. **RESTATE** understanding (1-2 sentences: "Con hiểu là Bố muốn...")
2. **LIST assumptions** explicitly ("Con giả định: A, B, C")
3. **ASK** clarifying questions if <100% confidence
4. **WAIT** for Warren approval → THEN act

If you are about to write a plan/spec and Warren has not explicitly confirmed "ok go ahead" with 100% clarity → STOP → load `interview-me` → ask one question at a time with GUESS + confidence → restate → confirm → THEN proceed.

**Ops-specific freeze examples:**

| Without freeze (dangerous) | With freeze (safe) |
|---|---|
| "Con sẽ tính revenue growth luôn" — assumes growth = (W32-W31)/W31 | "Con hiểu Bố muốn revenue growth. Con giả định công thức = (W32-W31)/W31. Đúng chưa ạ?" |
| "Đã fix parser xong" — assumes bug là do cột mới | "Con thấy parser bể. Con giả định nguyên nhân là GSheet pivot thêm cột. Con check trước khi sửa nhé?" |
| "Dashboard done" — assumes chart type đúng | "Con sẽ dùng bar chart cho revenue trend. Bố muốn bar hay line ạ?" |

**Red flag:** "this is simple, I'll just do it" → FREEZE anyway.

**🔓 PROCEED signal (Warren 2026-07-27):** Khi Bố gõ **"làm tiếp" / "tiếp tục đi" / "tiếp tục nào" / "approved" / "làm đi"** → Bố ĐÃ duyệt rõ ràng → Con THỰC THI NGAY, KHÔNG restate/hỏi lại. Freeze gate chỉ áp dụng khi yêu cầu CHƯA rõ (confidence <100%). Nếu Bố đã nói "làm tiếp" sau con báo cáo plan → coi như 100% approved → execute step tiếp theo luôn.

---

### ⚙️ Step-by-Step Execution Gate

**HARD RULE:** Every execution plan MUST be broken into discrete steps. Warren approves one step → Hermes executes → **verifies result** → reports → THEN proceeds to next step.

Pattern:
```
1. Propose plan as ordered steps with expected output per step
2. Warren: "ok go ahead"
3. Execute step 1 → verify → report result
4. Warren: "ok" → proceed to step 2
5. Execute step 2 → verify → report result
...repeat...
```

**Do NOT:** batch unverified steps, skip verification, assume prior "ok" covers future steps, present "done" without verification evidence.

Applies to ALL Warren interactions — operations, code, config, deployments.

---

### 📜 Spec-Kit Constitution Gate

**When:** New project/feature with lasting governance rules (auth, data policy, naming/stack, budget/API, compliance). Not for one-off fixes.

**Rules:**
- Run **once per project**, before ideation
- Store at `.specify/templates/constitution.md` (Spec-Kit) or `vault/_docs/<project>-constitution.md`
- **Do NOT silently overwrite** existing constitution — surface delta to Warren for re-ratification
- Non-IT framing: "Luật chơi" của dự án — ranh giới đỏ/được phép/không được phép

---

### ✅ Spec-Kit Checklist Gate

**When:** After `spec-driven-development`, before `planning-and-task-breakdown`.

**Output:** `PASS` with minor notes, or `BLOCKED` with exact missing items.

**Minimum checklist:**
- [ ] Objective and user story exist
- [ ] Assumptions are explicit
- [ ] Boundaries defined: Always / Ask first / Never
- [ ] Success criteria are testable
- [ ] Open questions resolved or deferred with owner

**Rules:** Keep 1 screen max. Never re-ask answered questions. If blocked → STOP before planning.

---

### 🔍 Spec-Kit Converge Gate

**When:** After `battle-test` + `ab-test`, before `code-review-and-quality`. Reconcile FIRST so review runs once on reconciled code.

**Output:** Delta report — 3 buckets:
- **Implemented as spec'd** — matches plan/tasks/spec
- **Missing** — task/spec item not built
- **Drifted** — built but different from spec/config/assumptions

**Rules:**
- Compare **spec → plan → tasks → built artifacts**, not just spec vs code
- Require Warren acknowledgment before review/commit if `Drifted` or `Missing` non-empty
- Must be clean before final review

---

## Spec-Kit Workflow (Strict Sequence)

When Warren asks for a feature/change and the interview gate is cleared, follow this EXACT order:

```
0o. speckit-constitution   — đặt nguyên tắc dự án (1 lần/dự án)
1. idea-refine           — Expand concept, generate variations, converge
2. spec-driven-development — Write spec with assumptions, get Warren's review
2s. speckit-checklist      — Checklist artifacts sau spec, TRƯỚC planning
3. planning-and-task-breakdown — Breakdown tasks, dependency graph, phases
4. incremental-implementation — Build slice by slice, test each slice
5. Verification          — Ad-hoc script or pytest (see battle-test skill: calculation functions → pytest, integration → vanilla)
6. battle-test           — 5 adversarial situations + stress + edge cases
7. ab-test               — Before vs After comparison, declare winner
8. speckit-converge        — Đối chiếu code vs spec/plan/tasks, TRƯỚC review
9. code-review-and-quality — 5-axis review (correctness, readability, arch, security, perf)
10. code-simplification  — Simplify patterns, remove dead code
   ⚠️ Steps 9-10 có thể chạy song song subagents; re-read sau khi cả 2 xong.
11. git-workflow-and-versioning — ALWAYS ask Warren before commit/push with summary.
```

Key rule: `git-workflow-and-versioning` is LAST. Do NOT commit before Warren approval.

Spec-Kit gates are additive only. Existing Warren gates (interview-me, step-by-step verify, incremental implementation/review/simplification) are unchanged.

---

### ⚠️ Skill Maintenance & External-Skill Integration Pitfalls

1. **Ops vault ≠ no-code.** Warren's vault contains real code — parsers (`luso-parsers`), dashboards, pipelines (`warren-ops-pipeline`), `verify-parser-output`. Code skills ARE applicable whenever Warren asks to build a parser/script.

2. **Check the skill path BEFORE patching.** Skills live in two trees:
   - `C:/Users/khoans/AppData/Local/hermes/skills/common/...` → **bundled** (DO NOT EDIT — overwritten on Hermes update)
   - `C:/Users/khoans/AppData/Local/hermes/profiles/warren-profile/skills/...` → **custom** (editable)
   To change a bundled skill: create **override wrapper** in `warren-profile/skills/`; never patch in place.

3. **Verify capability isn't already present under a different name.** Grep first, absorb external mechanics into existing Warren skill rather than creating parallel copies. Only ADD when Warren genuinely lacks the capability.

4. **Prefer dedup over add.** Absorb external skill *mechanics* into existing Warren skill (keeping Warren Gates) rather than installing parallels.

5. **Custom skills are NOT in the vault git repo — back them up.** After editing any custom skill, copy changed file(s) to `vault/_archives/skills/<skill>_<file>_backup_YYYY-MM-DD.md`. Do NOT `git init` inside skills folder — data-exfiltration risk on company laptop.

6. **`patch` replace-vs-insert khi sửa bảng routing (học 2026-07-29):** Khi thêm dòng vào bảng routing dùng `patch`, old_string khớp dòng hiện có → bị REPLACE thay vì INSERT. Fix: old_string phải chứa dòng MỚI + dòng BÊN DƯỚI, new_string = dòng mới + dòng bên dưới. Mẫu: `old_string="| Dòng sát trên | ... | If ... |"`, `new_string="| Dòng mới | ... | If ... |\n| Dòng sát trên | ... | If ... |"`. Áp dụng mọi lần patch bảng routing của safenet/qa-gate/skill khác.

## Post-Skill Output Template (mandatory, apply every create/edit/patch/delete)

**HARD RULE:** After ANY skill create/edit/patch/delete, GG MUST print this exact template in chat — no exceptions.

```markdown
✅ Skill created/updated: `<name>`

🔑 SSOT (chỉnh sửa ở đây):
`vault/.scripts/skills/<name>/SKILL.md`

🪞 Runtime mirror (tự động sync, KHÔNG chỉnh trực tiếp):
`AppData/.../skills/<name>/SKILL.md`

📦 Archive backup:
`vault/_archives/skills/<name>_SKILL_backup_YYYY-MM-DD.md`

🔄 Diff: ✅ identical
```

**Rules:**
- **SSOT path = `vault/.scripts/skills/<name>/SKILL.md`** (có dấu chấm `.`, git-backed). Mọi sửa PHẢI ở đây.
- **Runtime path = `AppData/.../skills/<name>/SKILL.md`** (KHÔNG có dấu chấm, KHÔNG backup, KHÔNG git). Chỉ copy 1 chiều từ SSOT.
- **Backup path = `vault/_archives/skills/<name>_SKILL_backup_YYYY-MM-DD.md`** — mandatory sau mỗi change.
- **Diff MUST be identical** trước khi báo "sync✓".
- **KHÔNG bao giờ edit AppData trực tiếp** — bị ghi đè khi sync từ SSOT.

7. **Delegation sizing — split big fan-out (2026-07-26).** `delegate_task(tasks=[...])` với N goals + nội dung lớn (>~8K tokens/gọi) → **stream timeout, không deliver**. FIX: dispatch **N call lẻ** (mỗi agent 1 `delegate_task`), chạy song song nền tự nhiên. Áp dụng khi Bố bảo "chạy 4-agent review" / "deep review đa trục" → con gọi lẻ từng cái thay vì 1 batch. Con vẫn tổng hợp findings sau.

8. **Quality-pipeline composition (2026-07-26).** Khi Bố bảo chuỗi "improve + ab-test + debug + simplify + review" → chạy ĐÚNG THỨ TỰ, mỗi bước có verify gate:
   `improve-codebase-architecture` (audit) → `ab-test` (A vs B) + `debugging-and-error-recovery` (nếu có bug) → `code-simplification` (inline, rẻ) → `simplify-code` (4-agent deep, CHỈ khi Bố gọi tường minh) → `code-review-and-quality` (5-axis). Luôn **TDD trước** (red→green) khi có code mới. Không dọn code chưa chạy.
   - **qa-gate integration (2026-07-29):** `qa-gate` được gọi TỰ ĐỘNG bởi safenet §D trước reviewer-node. 🟢 → qa-min (verify-parser + ab-test). 🟡/🔴 → qa-full (+ battle-test + speckit-converge). PASS → reviewer-node. FAIL → BLOCKED. KHÔNG cần gọi tay.
 ▶ Chi tiết gotchas thực tế (delegation split, markdown delimiter, registry extensibility, TDD fixture): `references/quality-pipeline-gotchas.md`.

   - Workflow SKILL.md PHẢI có bước spawn `reviewer-node` (fresh context, `delegate_task`) review output trước khi báo Warren. Không chỉ依赖 global `safenet` §D — ghi thẳng vào SKILL.md = structural guarantee (skill tự có critic, không dựa agent nhớ).
  - Pair với `verify-parser-output` (independent recompute + cross-assert) cho parser trước khi qua reviewer.
  - `reviewer-node` là skill GLOBAL — gọi qua delegate_task, KHÔNG embed copy (tránh duplicate drift).
  - **`simplify-code` 4-agent fan-out: delegate_task max 3 concurrent → chạy batch 3 + 1 lẻ (không pass 4 tasks 1 lần, lỗi "Too many tasks: 4").** Đã áp dụng 2026-07-27.
9. **Map vs Gate — đừng nhét execution gate vào router (2026-07-29).** `using-agent-skills` là BẢN ĐỒ (router) — nó BIẾT skill nào tồn tại, KHÔNG THỰC THI chúng. Nhét QA logic vào đây = router 500+ dòng, không ai dám sửa, gate không hoạt động vì logic nằm sai chỗ. Pattern đúng: 3 tầng tách biệt — Router (using-agent-skills) → Gate executor (qa-gate, safenet) → Skill chuyên môn (verify-parser-output, ab-test...).

---

## 🧬 Matt Pocock Techniques — Absorbed (deep-dive 22 SKILL.md, 2026-07-25)

> Nguồn: `github.com/mattpocock/skills` (bộ "Skills For Real Engineers"). Warren duyệt gom hết vào 1 lệnh này (thay vì 3 lệnh router) để Bố chỉ nhớ 1 chỗ. Mỗi technique đi kèm "dùng khi nào" — Con tra cứu mục này khi task khớp.

### Taxonomy (từ README)
- **User-invoked** = chỉ chạy khi Bố gõ tên (vd `interview-me`). **Model-invoked** = Con tự trigger khi task khớp (vd `verify-parser-output`, `safenet`). → Biết 1 skill thuộc loại nào giúp Con không tự chạy sai zone.

### 12 Techniques (absord, không tạo skill mới)

| # | Từ skill Matt | Technique + Dùng khi nào |
|---|---|---|
| 1 | **wayfinder** | **Decision Map + fog-of-war** — tách phase "quyết định" khỏi "thực thi"; 1 quyết định/1 phiên; map chỉ gist+link. → Dùng cho **initiative lớn** (mở store, đổi POS, tái cấu trúc P&L): chưa nhìn thấy đường → lập Decision Map trước, đừng nhảy vào làm. |
| 2 | **to-tickets** | **Expand–Contract** cho đổi quy trình toàn chuỗi + vertical-slice + Blocked-by/frontier. → Đổi menu/quy trình 3 store = chạy song song cũ+mới → migrate từng store → tắt cái cũ. Mỗi bước phải demo/kiểm chứng độc lập. |
| 3 | **triage** | State machine 5 trạng thái (cần-xem / chờ-thêm-info / agent-làm-được / Bố-quyết / không-làm) + **out-of-scope log** (ghi lý do từ chối để từ chối nhất quán). → Luồng yêu cầu/complaint/idea từ store managers LU3/LU5/LU7 đổ về. |
| 4 | **diagnosing-bugs** | Dựng **feedback loop / cách verify CHẶT trước khi đưa giả thuyết** + liệt kê 3–5 giả thuyết xếp hạng, mỗi cái **falsifiable** (có prediction). → "Sao doanh thu LU3 tuần này sai?" → reproduce được trước, liệt kê giả thuyết bác-bỏ-được, không đoán mò. |
| 5 | **tdd** | **Anti-pattern "tautological"** — verify số bằng nguồn ĐỘC LẬP, KHÔNG tính lại cùng công thức. → `verify-parser-output`: đối chiếu tổng doanh thu với 1 nguồn khác, không cộng lại y hệt cách parser tính. |
| 6 | **domain-modeling** | **Tiêu chí 3-điều-kiện để ghi 1 decision record**: khó đảo ngược + gây ngạc nhiên + là kết quả trade-off thật. → Biết KHI NÀO đáng ghi 1 quyết định vào vault (không ghi mọi thứ). |
| 7 | **improve-codebase-architecture** | **Deletion test** ("bỏ parser/file này thì việc phức tạp hơn hay chỉ dời chỗ?") + **scope theo hot spots** (file/pipeline hay đổi gần đây — YAGNI). → Audit vault/parser pipeline. |
| 8 | **ask-matt** | **Context-hygiene**: giữ grill→plan→ticket trong 1 session liên tục, KHÔNG compact giữa chừng; mỗi lần thực thi thì mở session mới sạch; ngưỡng "smart zone" (~120k tokens). → Khi làm initiative dài, đừng để Con compact mất ngữ cảnh giữa các phase. |
| 9 | **to-spec** | "Spec chỉ ghi QUYẾT ĐỊNH, link SSOT, KHÔNG copy chi tiết dễ lỗi thời" + **Out-of-Scope bắt buộc** trong mọi plan. → Viết spec/plan/proposal: không ghi số điện thoại NV, giá tạm… vào plan — link về SSOT thay. |
| 10 | **prototype** | "Capture verdict + câu hỏi nó settle" — mọi pilot/thử nghiệm phải ghi lại nó đã trả lời câu hỏi gì. → Chạy pilot nhỏ 1 tuần 1 store trước khi rollout 3 store (`explore`). |
| 11 | **code-review** | "2 trục Standards vs Spec báo cáo TÁCH BIỆT, không rerank chéo" (code có thể pass chuẩn nhưng fail spec). → Review 1 deliverable ops: (a) đúng convention/format vault vs (b) đúng cái Bố/sếp thật sự yêu cầu. |
| 12 | **setup-…-skills** | Phỏng vấn setup "recommended-answer-first, 1 section 1 câu, skip khi đã tự trả lời". → Onboard workflow mới (`new-automation`): trình phát hiện, Bố gật 1 chữ là xong. |

### 📋 CẦM TAY: TẠO SKILL / PARSER / SCRIPT MỚI (non-IT, copy-paste)
> Thứ tự gõ lệnh. Nguyên tắc vàng: không rõ → hỏi, đừng đoán. Mọi file mới → Bố duyệt trước khi Con ghi (zone 🟡).
> Luật bất di bất dịch: (1) LU7 mở 10h = luật mall, KHÔNG chê LU7 làm kém; (2) Doanh thu chỉ lấy từ SSOT (`09_Hourly`+`01_Weekly`), KHÔNG từ COL; (3) Mọi số phải qua kiểm tra độc lập.

| Bước | Bố gõ | Con làm | 🧬 Mẹo Matt (trên) |
|---|---|---|---|
| 0 | *(mở session)* | Bootstrap tự chạy | #8 ask-matt: giữ nguyên 1 session, đừng để Con compact mất ngữ cảnh |
| 1 | `interview-me <ý>` | Hỏi từng câu + có gợi ý → chốt ý | #10 prototype: pilot nhỏ 1 store thử trước khi roll 3 store |
| 2 | `spec-driven-development <ý>` | Viết đề bài 6 phần | #9 to-spec: chỉ ghi QUYẾT ĐỊNH, link SSOT + #6 domain-modeling: chỉ ghi decision record khi đủ 3 điều kiện |
| 3 | `planning-and-task-breakdown` | Bẻ nhỏ + ghi bước nào chặn bước nào | #1 wayfinder: initiative lớn → lập Decision Map trước + #2 to-tickets: Expand–Contract |
| 4 | *(tự động)* | Tick `parser_script_checklist` (LU7 10h, revenue SSOT, format M, data ≥4 tuần) | — |
| 5 | `incremental-implementation` | Làm từng lát → show → Bố "tiếp" | — |
| 5b | *(HTML dashboard)* | **VERIFY `</script>` đóng + node syntax check** — file HTML có inline `<script>` PHẢI có thẻ `</script>` đóng trước `</body>`; thiếu → Chrome báo `Unexpected token '<'` → drop toàn bộ script, chart trắng. Chạy `node -e` parse script block bắt JS error. | — |
| 6 | *(tự động)* | **`battle-test`** — thử 5 tình huống xấu + quá tải | — |
| 7 | *(nếu bể)* | **`debugging-and-error-recovery`** — sửa | #4 diagnosing-bugs: dựng cách verify CHẶT trước khi đoán + liệt kê 3–5 giả thuyết bác-bỏ-được |
| 8 | *(tự động)* | **`ab-test`** — so Before vs After, chốt ai thắng | — |
| 9 | *(tự động)* | `speckit-converge` — đối chiếu code vs spec | — |
| 9b | *(tự động)* | **`qa-gate`** — tổng hợp test → PASS/FAIL. 🟢 = qa-min (verify-parser+ab-test), 🟡/🔴 = qa-full (+battle-test+speckit-converge). FAIL = BLOCKED. Gọi bởi safenet §D. | — |
| 10 | `code-review-and-quality` | Review 2 trục | #11 code-review: 2 trục (đúng chuẩn vault / đúng cái Bố thật sự muốn) báo RIÊNG |
| 11 | `dọn code` / `simplify-code` | Dọn NHẸ (rẻ) hoặc sâu 4 tầng | #7 improve-codebase-architecture: deletion test + ưu tiên chỗ hay đổi gần đây |
| 12 | *(có số thì tự động)* | `verify-parser-output` | #5 tdd: verify bằng nguồn ĐỘC LẬP, KHÔNG tính lại cùng công thức |
| 13 | *(tự động)* | `reviewer-node` soi lại (CHỈ sau qa-gate PASS + zone 🟡/🔴) | — |
| 14 | `handoff` *(nếu dở dang)* | Lưu state | — |

**3 trường hợp đặc biệt:** (A) Muốn tự động → `new-automation` (có #12 setup: hỏi kèm gợi ý, Bố gật 1 chữ là xong). (B) Test tool lạ → `explore`. (C) Bối rối → `using-agent-skills` (đã gom đủ 12 mẹo trên).
**Thứ tự debug vs simplify:** battle-test → debug (nếu hỏng) → ab-test → review → **simplify-code CUỐI CÙNG** (đừng dọn code chưa chạy).

### SKIP (đã cover / code-specific / chưa nhu cầu)
`grill-me`·`grill-with-docs`·`grilling` (interview-me đã absorb) · `implement` (incremental-implementation sâu hơn) · `research` (deep-research) · `handoff`·`writing-great-skills` (vault superset) · `codebase-design`·`resolving-merge-conflicts` (thuần code/git) · `teach` (chưa có use case training staff).

---

## 🔗 Skill Chaining & Ops Notes (2026-07-26)

### A — Common Skill Chains (copy-paste khi Bố gõ chuỗi)
- **Build parser/pipeline:** `using-agent-skills` → `incremental-implementation` → `test-driven-development` → `writing-great-skills` → (quality) `improve-codebase-architecture` → `ab-test` → `debugging-and-error-recovery` → `code-simplification` → `simplify-code` → `code-review-and-quality`.
- **Absorb external methodology (học 2026-07-29):** `external-repo-eval` (deep-dive + subagents) → `spec-driven-development` (viết spec absorption) → `planning-and-task-breakdown` (vertical slices) → `incremental-implementation` (patch từng slice) → `ab-test` (before vs after) → `qa-gate` (qa-min: verify + ab-test) → `git-workflow-and-versioning` (commit/push). Mỗi slice = 1 file skill, verify sau mỗi patch bằng `diff -q` SSOT vs runtime. Không tạo skill mới trừ khi concern KHÁC hoàn toàn.
- **Rule:** mỗi skill load context riêng. Chạy TUẦN TỰ, BÁO CÁO từng bước, Bố duyệt mới bước sau. YAGNI: chỉ load skill cần, đừng load cả 6 quality-skills nếu chỉ cần 1.

### B — delegate_task quota = 3
- `max_concurrent_children` mặc định = **3**. `simplify-code` đòi 4-agent fan-out → phải split **batch 3 + 1** (pass 4 tasks 1 lần → lỗi "Too many tasks: 4").
- **⚠️ HARD RULE (real failure 2026-07-28):** default `max_concurrent_children` = 3, KHÔNG PHẢI 4. Skill `simplify-code` (BUNDLED, GG không sửa được) có đoạn claim *"Four is the right fan-out... it's within the delegation.max_concurrent_children budget on any default install"* LÀ SAI và sẽ gây lỗi thực tế: `Too many tasks: 4 provided, but max_concurrent_children is 3`. Recovery BẮT BUỘC: tách thành 2 call — `delegate_task(tasks=[3 vai])` trước, rồi `delegate_task(tasks=[1 vai])` sau. Không pass 4 trong 1 mảng.
- (Liên quan: pitfall #7 — split big fan-out thành N call lẻ cũng được.)
- **🔒 Subagent scope containment (2026-07-27):** Khi delegate_task review/simplify, LUÔN liệt kê EXACT file paths trong `context` VÀ thêm dòng cứng: *"ONLY read these files; do NOT grep/search the broader repo or other modules."* Subagent có xu hướng lan ngoài scope (thực tế: REUSE-review agent tự grep `_week_utils.py` ngoài 2 file Bố chỉ định) → sinh finding out-of-scope, lãng phí context. Pair với scope-before-scan (improve-codebase-architecture §1): agent chỉ audit đúng vùng Bố gọi.

### C — execute_code blocked in cron-mode
- `execute_code` bị block (cron-mode profile) → dùng `terminal python -c` hoặc viết script file `.py` thay thế. Áp dụng mọi parser/skill run trong warren-profile cron session.

### D — Gate tokens vẫn áp dụng khi chain skill
- 🔰 SAFENET (🟢/🟡/🔴), 🧊 FREEZE (restate trước mỗi output non-trivial), 📦 ARCHIVE (sau mỗi tạo/sửa skill) → emit NGAY CẢ khi đang chạy skill chain (skill không auto-emit).

### E — Memory propose-only (warren-profile)
- Phát hiện durable fact trong skill chain → **ADVISE Bố, KHÔNG auto `memory()`**. Bố duyệt mới ghi. Built-in memory = propose-only (KHÔNG sync vào vault WARREN_MEMORY.md — compress-memory chỉ ghi vault SSOT).

---

## 📚 Governance & History

Các tài liệu về kiến trúc consent-gate, self-building loop, skill-creation pipeline, và các bug lịch sử đã chuyển vào **`references/governance.md`**. Chỉ load khi cần debug staging bug hoặc tra cứu quyết định thiết kế cũ. Không load mặc định để tiết kiệm context.

## Reference Files

- **`references/governance.md`** — Governance docs: consent-gate architecture, self-building loop, skill pipeline history, known staging bugs
- **`references/external-framework-evaluation.md`** — Research & evaluate external frameworks against Hermes ops stack
- **`references/lifecycle-example-lusine-ops.md`** — Proven patterns from past L'Usine ops sessions
- **`references/multi-profile-distribution.md`** — Multi-profile skill distribution protocol
- **`references/multi-vault-multi-bot-architecture.md`** — One bot = One vault architecture
- **`references/telegram-bot-pattern.md`** — Aiogram 3.x Telegram bot integration pattern
- **`references/vietnamese-slug-generation.md`** — Unicode NFD slug generation for Vietnamese
- **`references/windows-non-friction-automation.md`** — Windows .bat launcher and path patterns
- **`references/vault-separation-migration.md`** — Split shared vault into separate vaults + reversible migration
- **`references/hybrid-dashboard-architecture.md`** — Reusable vault dashboard structure