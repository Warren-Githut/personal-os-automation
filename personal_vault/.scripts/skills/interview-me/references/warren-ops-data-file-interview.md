# Warren Ops Data File Interview Pattern

## When to Use

When Warren (30yr F&B veteran, Head of Ops) asks you to review, audit, or redesign an operational data tracking file (Weekly Revenue Log, GrabFood Log, COL Log, etc.) — and the requirements are not 100% clear. This pattern extends the base `interview-me` skill with Warren-specific adaptations for ops data file design.

## Core Insight: FBM Role-Play Framing

Warren explicitly expects every GUESS and recommendation to be framed from the perspective of an **F&B veteran (30yr FBM)** — not a technical analyst. This means:

- Every GUESS must answer: *"What would a 30-year F&B operator care about here?"*
- Use domain-first reasoning: *"FBM nào cũng muốn biết channel mix đầu tiên"* — anchor every metric recommendation in its business decision value, not its technical elegance.
- Every recommendation must come with a concrete action attached, not just an observation.
- Token efficiency arguments are legitimate but must be secondary to business insight arguments.

## Interview Sequence

### Phase A: Initial Assessment (no questions yet)

Load the file, assess it FROM THE FBM PERSPECTIVE first:

1. **What business decisions does this file feed?** (ad budget, menu focus, staffing, pricing)
2. **What's missing that a 30yr operator would scream about?** (channel mix %, weekend vs weekday split, GP per order)
3. **What's wasting tokens?** (template instructions in data file, repeated boilerplate, empty columns, zero-data noise)
4. **Rate it**: 🟢 Good / 🟡 Adequate / 🔴 Needs work

Present assessment concisely — 3-5 bullets of what's working, 3-5 of what's not. End with 2-4 direction options (A/B/C/D).

### Phase B: One Question at a Time, FBM-Framed

Each question must have:
- **Q**: The focused question
- **GUESS**: Your hypothesis framed from FBM perspective, WITH concrete numbers where possible

**FBM Framing Examples (from real session):**

| Plain version | FBM version |
|---|---|
| "Should we add channel mix percentage?" | "Đây là cái mà FBM nào cũng muốn thấy đầu tiên — 'GF đang chiếm bao nhiêu phần bánh?' Tốn 80 chars, trả lời câu hỏi strategic quan trọng nhất." |
| "Should we keep the daily breakdown?" | "F&B operator cần biết thứ 7 là peak hay không — nhưng có cần 7 dòng/tuần không? 1 dòng high/low có đủ?" |
| "Should we add GP per order?" | "Hiện file dừng ở Net After Ad. Nhưng F&B operator cần biết: sau khi trừ food cost + commission + ad, mỗi order GF lời hay lỗ?" |

**When framing, always include:**
- **The decision it feeds**: "Cái này trả lời câu hỏi..."
- **The token cost**: "Tốn X chars"
- **The risk of NOT having it**: "Nếu ko biết channel mix → ko thể quyết định ad budget"

### Phase C: Concrete Template Visuals Early (Confidence Farmer adaptation)

Warren (Confidence Farmer archetype) needs to SEE the format before approving abstract proposals.

After 2-3 questions when format direction starts converging:
1. **Propose a minimal template** — 1 table + 1 diagnosis line, NOT full sections
2. Use markdown code block: `| Metric | LU3 | LU5 | LU7 |` style
3. Warren will correct columns, metrics, layout directly on the visual
4. **Create the output file early** — as soon as format is clear, write the scaffold (frontmatter + template + documentation). Don't wait for interview to finish. File = shared reference.

### Phase D: Key Constraints to Surface

For every ops data file redesign, always clarify:

1. **Reader priority** (human vs Hermes) — this determines EVERYTHING about format (JSON vs markdown, compact vs verbose)
2. **Critical business decisions** — rank the 3 most important decisions this file feeds
3. **Format enforcement** — is the template enforced by parser script or by manual discipline?
4. **Cross-file dependencies** — does this file need data from other files? (e.g. Channel Mix % needs Revenue Log)
5. **Token budget** — what's the waste-to-value ratio? Surface exact char counts when possible

### Phase E: Restate (only at 100% confidence)

Do NOT attempt a restate until all ambiguity is resolved. Warren will reject 80-95% restates. The restate must include:

```
- Reader priority: [e.g. 60% Hermes / 40% Warren]
- 3 key decisions: [ranked]
- Format changes: [specific: remove template, add channel mix, compact X]
- Token savings: [estimated chars saved]
- File creation: [new file needed? existing file update?]
```

Then ask: **"Đã đủ 100% chưa?"** If no, identify the remaining gap.

## Phase F: Existing Pipeline / SSOT Discovery (anti-fabrication gate)

Before proposing ANY data source, computation method, or "where does X come from" — you MUST verify against the actual vault, not guess.

### The failure this prevents
In a real session, when asked to design a Manpower SSOT with CPH (Cost Per Hour), the agent:
- **Fabricated a source**: invented "LU_COL_ENGINE_V4 GSheet" as the hours source for CPH.
- **Missed the existing pipeline**: `ops-cph` = `payroll_cph.py` + `col_cph.py` + `cph_config.py`, already computing CPH per 7-function segment from payroll Excel → `cph_result_YYYYMM.csv` → `CPH_Phan_Tich_Rolling.md`.

Result: agent proposed +5 lines of duplicate aggregation code and a false GSheet dependency. User caught it: *"check kỹ lại command ops-cph đi."*

### Mandatory discovery steps (run BEFORE proposing sources)
1. **User names a command/pipeline (e.g. "ops-cph", "/cph")** → `search_files` for it in `scripts/` + `wiki/` + `10_OPERATION_DATA/` FIRST. Read the actual script. Do NOT infer what it does from the name.
2. **Proposing a metric computation** → grep the vault for existing files computing that metric (e.g. "CPH", "cost per hour"). If a rolling file + pipeline already exists, that IS the SSOT for that metric.
3. **Consolidating into a new SSOT file** → enumerate which sub-metrics already have their own SSOT (CPH, COL, wage structure). **Cross-link them, do NOT recompute/duplicate.** The new file holds Plan + Actual-stock + Gap; CPH stays in its own file.

### Anti-fabrication rules
- Never invent a source (GSheet ID, DB, API) when unsure. If you don't know where data comes from, ASK or grep. A wrong source silently poisons every downstream report.
- When a file/sheet is mentioned by the user (e.g. "LU_COL_ENGINE_V4"), confirm its ROLE from the user before assigning it a job. The user may say "keep it" — it may be a different metric's source, not yours.
- If you must guess a source inside a GUESS, LABEL it as a guess and state the verification step: *"GUESS: hours from GSheet X — NEED CONFIRM: is X the hours source or something else?"*

### SSOT design principle (for Warren vault)
Single SSOT ≠ single file holding every metric. It means: one file is the ENTRY POINT / pointer for "manpower chuẩn", but sub-metrics chain to their own SSOTs via `[[wikilinks]]`. This keeps parsers non-duplicated and Hermes grep-able. Example: `Manpower_Master.md` (Block 1 = plan Warren giữ, Block 2 = actual sync payroll, Block 3 = gap/vacancy) + `→ [[CPH_Phan_Tich_Rolling]]` for CPH. Parser must `preserve Block 1` (never auto-overwrite the plan the human owns).

## FBM Reasoning Templates

When proposing or evaluating a metric, use this decision tree:

```
Is this metric actionable?
├── YES → Does Warren have the power to change it?
│   ├── YES → HIGH value. Include.
│   └── NO → Monitor only. LOW priority.
└── NO → Informational. Consider skipping or 1-liner.
```

Example: Commission % = actionable (negotiate with Grab). Weekend/Weekday split = actionable (adjust ad schedule by day). Channel mix = actionable (decide where to invest marketing energy).

## Anti-Patterns

| Don't | Do instead |
|---|---|
| Propose abstract format changes | Show the actual table/markdown template |
| Say "this saves tokens" without quantifying | Say "saves ~2k chars per read = ~30% of file" |
| Recommend a metric without saying what decision it feeds | "Channel mix % helps decide ad budget" |
| Accept "sounds good" as confirmation | Wait for explicit "approved" or "ok" |
| Try to restate at <100% confidence | Keep asking until Warren's reaction is predictable |
