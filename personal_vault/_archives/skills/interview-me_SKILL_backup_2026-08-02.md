---
name: interview-me
description: Extracts what the user actually wants instead of what they think they should want. One-question-at-a-time interview until ~95% confidence about the underlying intent. On the Warren profile it ALSO builds the project's domain model inline — updates 00_CORE_LOGIC/CONTEXT.md glossary and writes an ADR for each key decision. Use when an ask is underspecified ("build me X" without "for whom" or "why now"), when the user explicitly invokes ("interview me", "grill me", "are we sure?", "stress-test my thinking"), or when you catch yourself silently filling in ambiguous requirements before any plan, spec, or code exists.
argument-hint: "What are we clarifying?"
---

# Interview Me

## Overview

What people ask for and what they actually want are different things. They ask for "a dashboard" because that's what one asks for, not because a dashboard solves their problem. They say "make it faster" without a number to hit.

The cheapest moment to find this gap is before any plan, spec, or code exists. Once you've started building, switching costs are real, and the user will rationalize the wrong thing into a "good enough" thing. The misfit gets locked in.

This skill closes the gap before it costs anything. The other Define-phase skills assume you already know roughly what you want: `idea-refine` generates variations from an idea, `spec-driven-development` writes the requirements down, `doubt-driven-development` stress-tests a plan after you've drafted one. Interview-me is the part before all of those, where you ask one question at a time, with your best guess attached, until you can predict what the user is going to say before they say it.

## When to Use

Apply this skill when:

- The ask is missing at least one of: **who** the user is, **why** they want it, what **success** looks like, what the binding **constraint** is
- The request is conventional rather than specific ("build me X", "make it faster") and you can't unpack the convention without guessing
- You're tempted to start with assumptions you haven't surfaced
- The user hasn't said which value they're optimizing for when two reasonable ones are in tension (simplicity vs. flexibility, cost vs. speed)
- The user explicitly invokes: "interview me", "grill me", "before we start, are we sure?", "stress-test my thinking"

**When NOT to use:**

- The ask is unambiguous and self-contained ("rename this variable", "fix this typo")
- The user has explicitly asked for speed over verification
- Pure information requests ("how does X work?", "what does this code do?")
- Mechanical operations (renames, formats, file moves)
- You already have ≥95% confidence; re-read the stop condition below before assuming you don't

## Loading Constraints

This skill needs a live, responsive user. **Do not invoke in non-interactive contexts** like CI pipelines, scheduled runs, `/loop`, or autonomous-loop. If you're in one of those and the ask is underspecified, flag that as a blocker for the user instead of guessing.

## The Process

### Step 1: Hypothesize, with a confidence number

Before asking anything, write down your current best read of what the user wants in **one sentence**, plus an honest confidence number (0–100%):

```
HYPOTHESIS: You want a way to answer "how are we doing?" in standup, and "dashboard" was the convention that came to mind.
CONFIDENCE: ~30% — missing: who it's for, what "metrics" means in context, and what success looks like
```

The number forces honesty. If you wrote down a high number but can't actually predict the user's reactions to the next three questions you'd ask, the number is wrong. Start at the confidence level you can defend.

When confidence is below ~70%, append a brief reason on the same line — what's still unresolved or missing. This tells the user exactly what the interview needs to surface, and prevents the number from being a vague signal.

### Step 1.5: Coverage Map & Mode Selection (steal từ field-kit 0.2.0)

**Coverage Map** — theo dõi các dimension liên quan trong suốt interview, KHÔNG hỏi những gì đã có trong map:
- `objective` (mục tiêu), `constraints` (ràng buộc), `audience` (ai hưởng lợi), `preferences` (sở thích), `risks` (rủi ro), `success criteria` (thế nào là xong), `failure conditions` (thế nào là hỏng), `tradeoffs` (đánh đổi), `non-goals` (không làm gì).

**Mode Selection** — chọn 1 mode theo outcome, đổi mode khi evidence đổi:
- `Clarify` (làm rõ), `Discover` (khám phá preference), `Brief` (thành decision brief), `Decision` (chốt 1 quyết định), `Retrospective` (nhìn lại), `Profile` (xây profile user).
- Với Warren: mặc định `Decision` / `Brief` (Bố hay cần chốt nhanh, có template).

### Step 2: Ask one question at a time, each with a guess attached

Format:

```
Q: <one focused question>
GUESS: <your hypothesis for the answer, with the reasoning that produced it>
```

Wait for the user to react before asking the next question.

**Fact vs. decision split (steal từ mattpocock/grilling):** Nếu 1 thông tin giải được bằng cách **tự tra** (filesystem, env vars, vault grep, tool call) → **tự tra, KHÔNG hỏi**. Chỉ hỏi những gì là **DECISION** thuộc về Bố (ai, tại sao, success look like). Việc hỏi 1 fact có thể tự biết = lãng phí attention của Bố.

**Why one at a time, not a batch:**

- The user can't react to your hypotheses if you bury them in a list
- Batches encourage skim-reading and surface answers
- The third question often depends on the answer to the first; asking them all at once locks in the wrong framing
- The user's energy for thinking carefully is finite; spend it one question at a time

**Why attach a guess:**

- The user reacts faster to a wrong guess than they generate an answer from scratch
- It commits you to a hypothesis you can be visibly wrong about, which keeps you honest
- It surfaces *your* assumptions, which is what the interview is meant to expose

The risk here is a polite user agreeing with your guess to be agreeable. Mitigate by being visibly willing to be wrong, and occasionally guess in a direction you expect the user to push back on.

### Step 3: Listen for "want vs. should want"

The most dangerous answers are the ones where the user says what a thoughtful answer *sounds like* rather than what they actually want. Watch for:

- Answers that pattern-match best-practice talk ("I want it to be scalable", "clean architecture") without specifics
- Answers that defer to convention ("the way most apps do it", "the standard approach")
- Phrases like "I should probably…", "I think I'm supposed to…", "good engineering practice says…"
- Buzzwords as goals — when "modern", "scalable", "robust" are the answer instead of a specific outcome

When you hear these, the question to ask is:

> *"If you didn't have to justify this to anyone, what would you actually want?"*

That single question often does more work than the previous five.

### Step 3.5: Checkpoint (steal từ field-kit 0.2.0)

Sau **3–5 câu trả lời substantive**, dừng lại 1 nhịp: tóm tắt (a) confirmed facts, (b) current interpretations, (c) tensions (điểm mâu thuẫn), (d) remaining unknowns. Trình Bố để Bố sửa lệch trước khi đi tiếp. Với Warren (Batch-Answerer): checkpoint có thể gộp nếu Bố batch-answer nhiều câu 1 lượt.

### Step 4: Restate intent in the user's own words

When your confidence is high, write back what you now think the user wants. Keep it tight (5–8 lines), use their language where possible, and structure it so the user can confirm or correct line by line:

```
Here's what I now think you want:

- Outcome:      <one line>
- User:         <one line — who benefits>
- Why now:      <one line — what changed>
- Success:      <one line — how we know it worked>
- Constraint:   <one line — the binding limit>
- Out of scope: <one line — what we're explicitly not doing>

Yes / no / refine?
```

Including "Out of scope" is non-negotiable. Half of misalignment is silent disagreement about what is *not* being built.

### Step 4.5: Build domain model + ADR inline (Warren profile)

While the interview surfaces terms and decisions, do TWO things the default process does not:

1. **Update CONTEXT.md glossary** — `00_CORE_LOGIC/CONTEXT.md` (section "Glossary" or "Shared Language" if present; if not, add one). Add or sharpen domain terms as the user defines them. One line per term: `term: plain-language meaning`. This is the "shared language" — it cuts verbosity and token spend in later sessions.
   - Rule: only add terms the user actually used or corrected. Do NOT invent vocabulary.
   - If a term already exists with a different meaning, flag it and ask before overwriting.

2. **Write an ADR for each non-trivial decision** — save to `00_CORE_LOGIC/` (or `_cases/<case>/` if tied to a case) as `ADR_<YYYY-MM-DD>_<slug>.md` with YAML frontmatter `date`, `type: adr`, `decision: <one line>`. Body: Context → Decision → Consequences (cheap to revert? locks in what?).
   - Only write ADRs for decisions with real trade-offs (not "we'll use Python" — that's a given). Skip trivial calls.

**Completion criterion (Warren profile):** Interview is done when: (a) the default 95% Confidence Stop is met, AND (b) any new domain terms are in CONTEXT.md, AND (c) any real decision has an ADR on disk.

**Do NOT:**
- Invent glossary terms the user didn't say
- Write ADRs for trivial or reversible calls
- Save intent/ADR before the user gives an explicit yes (the default red flag still applies)

### Step 5: Confirm — explicit yes, not "whatever you think"

The gate is an explicit "yes." The following are **not** yes:

- "Whatever you think is best." → The user is delegating, which means they don't have 95% confidence either. Re-ask with two concrete options framed as a choice.
- "Sounds good." → Ambiguous. Ask: "Anything you'd refine?" Silence isn't confirmation.
- "Sure, let's go." → Often a polite exit, not an endorsement. Same follow-up.
- Silence followed by "okay let's start." → The user has given up on the interview, not converged. Stop and ask whether you've missed something.

If they correct you, fold the correction in and restate. Loop until you get an explicit yes.

### The 95% Confidence Stop

You're done when you can answer yes to this:

> *Can I predict the user's reaction to the next three questions I would ask?*

If yes, you have shared understanding. Stop interviewing and produce the restate. If no, you're not done; ask the next question.

This is a checkable test, not a vibe. It also has a floor: if you've gone several rounds and still can't predict, that's information about the ask, not a reason to keep grinding. Stop and tell the user: "I've asked X questions and I still can't predict your reactions. Something foundational is missing. Want to step back?"

## Classification & Report Contract (steal từ field-kit 0.2.0)

**Classification enum** — dùng đúng 1 verdict (thay vì chỉ dựa 95% stop):
- `READY TO PROCEED` — đủ evidence, chốt được.
- `PROCEED WITH ASSUMPTIONS` — thiếu 1 phần, nhưng Bố chấp nhận giả định.
- `PAUSED` — tạm dừng, chờ input.
- `STOPPED` — dừng hẳn.

Khi evidence chưa đủ, chọn verdict yếu hơn mức evidence hỗ trợ (KHÔNG over-claim). Với Warren: 95% Confidence Stop vẫn là FLOOR, verdict `READY TO PROCEED` chỉ khi Bố explicit "viết lệnh".

**Report Contract** — trả đúng 8 headings (theo thứ tự):
- Interview Outcome
- Objective
- Confirmed Context
- Constraints
- Preferences
- Tradeoffs and Decisions
- Unknowns
- Recommended Next Step

Phải phân biệt: confirmed facts / interpretations / warnings / blockers / unavailable evidence / approval-gated next actions.

## Output

The output of this skill is a **confirmed statement of intent**: the restate from Step 4, with an explicit yes from Step 5. That's the deliverable. Specs, plans, and task lists are downstream; they consume the intent this skill produces.

If the user wants the intent to persist (a multi-session project, a handoff to another collaborator), offer to save it to `docs/intent/[topic].md`. Only save if they confirm.

## Example

A short before-and-after.

**Without `interview-me`:**

```
User:  build me a dashboard for our metrics
Agent: <starts proposing chart libraries and layouts>
```

The agent has assumed: who it's for, what metrics, what "for our team" means, what success looks like. None of these are stated. Every assumption is a place the user can later say "that's not what I meant."

**With `interview-me`:**

```
User: build me a dashboard for our metrics

Agent:
HYPOTHESIS: You want a way to answer "how are we doing?" in standup, and "dashboard" came to mind because that's the conventional answer.
CONFIDENCE: ~30% — missing: who it's for, what "metrics" are, and what success looks like

Q:     When you say "how are we doing?", who's asking — you alone, the engineering team in standup, or up the chain (e.g., your manager, an exec, a board)?
GUESS: engineering team in standup, because "we" usually scopes that way and standups are where this question gets asked. If it's for execs the metrics and the framing change a lot.

User: It's actually for me. I keep losing track of which experiments are running and what their early signal looks like.

Agent:
Updated read: not a team dashboard at all. It's a personal experiment tracker. Confidence: ~60% — still missing: what "early signal" means and what done looks like.

Q:     Is the gap that you don't know which experiments exist, or that you can't see their results in one place?
GUESS: the second one. You have a list of experiments somewhere, but their results live in five different tools, and reconciling them by hand is what you're tired of.

User: First one actually. I literally don't have a list. They're spread across different docs.

Agent: <continues>
```

Two questions in, the agent has discovered the actual ask isn't "a dashboard." It's "a list." Different artifact, different scope, different work. The dashboard would have been wrong.

## Interaction with Other Skills

- **`idea-refine`**: downstream. If the confirmed intent is "I want X but I don't know how to scope it," hand off to `idea-refine` to generate variations against the now-explicit intent.
- **`spec-driven-development`**: downstream. If the confirmed intent is concrete ("I want X for Y users with Z success criteria"), hand off to `spec-driven-development` to write it down.
- **`planning-and-task-breakdown`**: two hops downstream of this skill (after the spec).
- **`doubt-driven-development`**: opposite end of the timeline. Interview-me is pre-decision intent extraction; doubt-driven is post-decision artifact review. Both catch divergence, but at different moments.
- **`source-driven-development`**: orthogonal. Interview-me clarifies what the user wants; SDD verifies framework facts. They don't compete.

### Handoff: Skill Creation Spec (Fresh Session)

When the confirmed intent is to create a Hermes skill and the user wants it done in a **fresh session** (clean context, no interview noise):

1. **Complete interview to 100%** — do NOT skip to spec early. The Confidence Farmer archetype rejects incomplete specs.
2. **Hold the spec inline in the conversation** — do NOT write to `_inbox/` (Warren rule 2026-07-14: anh implement luôn sau duyệt plan, ghi inbox là phí). The spec must be complete enough that a fresh Hermes session with zero context can read it and run `skill_manage(action='create')` without asking a single question back. Required sections:
   - Purpose (1-line outcome)
   - Core rules (SOPs, constraints, banned patterns)
   - Input format with real examples for every variant
   - Output format template (exact markdown structure)
   - Platform/type detection logic
   - Operational matrix (decision tree, paths, thresholds)
   - External integration details (API endpoints, auth, sheet IDs, column maps)
   - Workflow diagram (ASCII)
   - Constraints & out-of-scope
   - Full worked example (input → output)
3. **Do NOT create the skill in the same session** — the user explicitly wants it in a fresh session. Just deliver the spec inline (paste it into the fresh session, or put it in the skill's `references/` dir if a durable artifact is needed — never `_inbox/`).
4. **User instruction for fresh session:** "Tạo skill `<name>` từ spec này (đã được paste / nằm trong `references/`)."
5. The spec language must match vault language policy (Vietnamese có dấu for L'Usine vault).

**Pitfall:** If the spec is missing even one edge case that was resolved during interview, the fresh session will either guess wrong or ask the user, breaking the "non-friction" promise. Every Q&A from the interview must be encoded in the spec.

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "The ask is clear enough" | If you can't write the user's desired outcome in one sentence right now, the ask isn't clear. Run Step 1 before deciding. |
| "Asking too many questions wastes their time" | Time wasted by 4–6 targeted questions is small. Time wasted by building the wrong thing is enormous, and the user is the one bearing that cost. |
| "I'll figure it out as I build" | Switching costs after code exists are 10x what they are now. Discovery during implementation is rework. |
| "They said 'whatever you think,' so I should just decide" | "Whatever you think" is delegation, not decision. Re-ask with two concrete options as a choice. |
| "I should give them several options to pick from" | Options work when the user knows what they want and is choosing between trade-offs. They don't know what they want yet. Listing options widens the search; asking narrows it. |
| "If I attach my guess, I'm leading them" | Leading is the point. Reacting is faster than generating from scratch. The risk is sycophancy, not leading; mitigate by being visibly willing to be wrong. |
| "We've talked enough, I get it" | Test it: can you predict their reaction to the next three questions? If not, you don't get it yet. |
| "The user said yes, we're done" | If the yes followed a vague restate or an open-ended "sounds good," the yes is hollow. Restate concretely and re-confirm. |

## User Archetypes & Adaptation Patterns

The base process assumes a general user. These patterns emerged from real sessions and override the default approach when recognized.

### Archetype: Numerical Fixer (e.g. Warren)

The user corrects weights, thresholds, and percentages **immediately and precisely** — not "that's wrong" but "change 20 to 25, MOS >20%→>10%".

**Patterns:**
- They will correct your numbers mid-sentence, sometimes before you finish writing the GUESS.
- When they correct a number, they give the **exact replacement value** — take it, update, and move on. Do not justify why you chose the original number.
- They expect every GUESS to have concrete numbers attached. Abstract GUESSes without thresholds are treated as noise.
- If you fail to include a number in a GUESS, they will call it out explicitly (e.g. "hãy cho tao biết mức độ quan trọng của từng chỉ số").

**Adaptation:**
- Every GUESS must contain at least one quantitative threshold. "GUESS: high quality" is insufficient. "GUESS: 20/20 for moat ± 5% tolerance" is correct.
- When corrected, acknowledge the number, update your model silently, and move to the next question. Do not explain — their correction IS the explanation.

### Archetype: Batch-Answerer (e.g. Warren)

The user does not wait for one-question-at-a-time sequencing. They answer Q1 early, add Q2 context, and sometimes answer Q3 before you've asked it.

**Signals:**
- A single user turn contains multiple answers that would have spanned 2-4 of your planned questions.
- They skip over a question you asked and answer a different one they find more important.
- They interleave answers to past questions with new questions of their own.

**Adaptation:**
- Do NOT insist on "one question at a time" formatting. This is a user-communication style, not a mistake.
- When they batch-answer, identify which of your planned questions are now answered and which are moot. Adjust confidence upward for answered questions.
- If a batch-answer makes a pending question irrelevant, state that and move on: "Q3 is now moot — you already answered it. Next question: ..."
- **Exception retained:** still ask ONE question at a time in YOUR turns. The constraint is on you, not on them. They can batch; you must not.

### Archetype: Confidence Farmer (e.g. Warren)

The user explicitly demands high confidence (>95%) before any execution. They will reject output at 65%, 80%, even 90% if the last remaining ambiguity isn't resolved.

**Signals:**
- They say "chừng nào 100% confidence thì mới viết lệnh" or equivalent.
- They push back on intermediate confidences: "confidence đủ 100% chưa?" after you declared 95%.
- They escalate unfinished questions into blockers rather than proceeding with assumptions.
- **They want to SEE a concrete template/visual before deciding.** Abstract proposals are not enough — they need to see the actual format, table structure, or report layout. "Show me the template first" is a strong signal. [Added 2026-07-02]
- **They say "ghi cụ thể vào file"** — they want the output artifact created EARLY and populated progressively as the interview proceeds. The file is the source of truth; the conversation is transient. "ghi cụ thể những cái bạn mới diễn giải ra, để sau này tôi mở file, tôi biết nó là gì" is a direct signal. When you hear this, create the file immediately with what you know so far, then iterate. [Added 2026-07-03]
- **They approve file creation promptly.** When offered a file scaffold, they say "tạo nhé" without hesitation. This is NOT premature execution — it's the preferred workflow: create early, iterate during the interview, finish with the interview. [Added 2026-07-03]

**Adaptation:**
- The 95% Confidence Stop is a FLOOR for this user, not a target. Keep going until you can predict reactions to the NEXT SIX questions, not just three.
- **Do NOT present a restate until confidence is exactly 100%.** A restate at 80-90% wastes the user's time — they will tell you to finish the interview first. Keep asking questions, don't attempt the restate until all ambiguity is resolved.
- After each restate, explicitly ask: "Đã đủ 100% chưa?" If they say no, identify what's still loose.
- Track the interview question count. If you pass Q8+ without convergence, stop and ask: "I've asked 8+ questions and still below 95%. Do we need to step back or is there one specific gap I'm missing?"
- Do NOT produce a draft/spec/skill until they explicitly say "go ahead" or "viết lệnh" — anything less is not confirmation.
- **Interleave a concrete visual early.** When discussing a data structure or report format, PROPOSE A VISUAL (markdown table, template code block, or file snippet) before asking "is this format OK?" This is faster than describing in prose — Warren will correct columns, metrics, or layout directly on the visual, which is more precise than abstract approval. [Added 2026-07-02]
- **Keep the template minimal on first pass.** Show 1 key table + 1 diagnosis line, not full sections. Warren will say "cần thêm X" if he wants more — start lean. [Added 2026-07-02]
- **Create the output file early, not at the end.** When the interview covers a concrete deliverable (a tracking file, a report), create the file scaffold (frontmatter + template + documentation) as soon as the format is roughly clear. Populate it with documentation of data sources, data flow, and setup instructions as they emerge from the interview. Do NOT defer file creation until the interview is complete — the file becomes the shared reference that makes subsequent questions faster. [Added 2026-07-03]
- **Accept immediate file creation when offered.** If Warren says "tạo nhé" after seeing a template, create it right away — don't wait for the interview to finish. The file is iterative, not final. [Added 2026-07-03]

### When the archetypes overlap

Warren exhibits all three simultaneously. The combined adaptation:
1. Put concrete numbers in EVERY GUESS, framed as **domain-expert business recommendations** (not technical hypotheses). If Warren has explicitly requested a specific role-play hat (e.g. "30yr FBM", "F&B veteran", "CEO perspective"), load `references/warren-ops-data-file-interview.md` BEFORE starting questions — it contains the FBM framing patterns. The GUESS must answer "what would a domain expert recommend?" not just "what do I think Warren will say?"
2. **State the role explicitly at the start of each assessment.** When Warren says "với vai trò là 1 fbm có 30 năm kinh nghiệm" or similar, open your response with the role label: "30 năm F&B đây." or "FBM hat on." This signals that every subsequent GUESS comes from that role's business judgment, not generic analysis. Do NOT silently adopt the role — declare it.
3. Accept batch-answers without pushing back on format.
4. Don't stop until explicit "viết lệnh" — "sounds good" is not enough.
5. When corrected, take the number and move — zero explanation overhead.
6. When the topic is an ops data file (tracking log, report, KPI sheet), check whether the `warren-ops-data-file-interview.md` reference applies — FBM framing is the expected default for ops file reviews. **Proactively offer a visual dashboard (Chart.js HTML) + centralized index when proposing format changes**, especially when the user is a visual learner — this emerged mid-interview as a natural extension of the Confidence Farmer archetype's need for concrete visuals.
7. **Do not attempt a restate until 100% confidence.** Presenting a restate at 80-95% will be rejected with "hãy make sure confidence là 100% thì hãy restate." Run the interview to completion before writing up the restate.

## Red Flags

- Three or more questions in a single message: that's batching, not interviewing
- A question without your hypothesis attached: that's surveying, not committing
- Accepting "whatever you think is best" as a terminal answer
- Producing a spec, plan, or task list before the user has explicitly confirmed your restate
- Questions framed as "what would be best practice?" instead of "what do you actually want?"
- The user gives a sophistication-signaling answer ("scalable", "clean", "modern") and you accept it without probing whether it's what they actually want
- Three or more rounds without your confidence visibly rising: you're asking the wrong questions, step back and reframe
- A confidence number below ~70% with no reason attached: the user can't help close the gap if they don't know what's missing
- Saving the intent doc before the user has confirmed (the doc itself implies a yes the user didn't give)
- Skipping the "Out of scope" line in the restate (silent disagreement about non-goals is half of misalignment)

## Reference Files

- **`references/warren-ops-data-file-interview.md`** — FBM role-play adaptation for interviewing Warren about ops data file design. Load when the interview task involves reviewing/redesigning operational tracking files (GrabFood Log, Revenue Log, COL Log, etc.) and Warren has asked for FBM-perspective analysis.
- **`references/ops-data-file-design-heuristics.md`** — 9 reusable design heuristics for ops data files (60/40 machine-human split, embedded JSON block, top 80% groups, scorecard format, accumulation JSON fallback, dashboard auto-rebuild). Apply AFTER interview is complete, during the design/build phase.

## Verification

After applying interview-me:

- [ ] An explicit hypothesis with a confidence number was stated in the first turn
- [ ] Every confidence number below ~70% was accompanied by a one-line reason (what's still unresolved or missing)
- [ ] Questions were asked one at a time, each with the agent's guess attached
- [ ] At least one "what would you actually want if you didn't have to justify it?" probe ran when the user gave a sophistication-signaling or convention-signaling answer
- [ ] A concrete restate (Outcome / User / Why now / Success / Constraint / Out of scope) was written back to the user
- [ ] The user confirmed the restate with an explicit yes (not "whatever you think," not "sounds good," not silence)
- [ ] (Warren profile) Any new domain terms surfaced during the interview were written to the CONTEXT.md glossary
- [ ] (Warren profile) An ADR was written for each non-trivial decision (Context → Decision → Consequences)
- [ ] At the stop point, the agent could predict reactions to the next three questions it would ask
- [ ] Any handoff to a downstream skill (`idea-refine`, `spec-driven-development`) was framed in terms of the confirmed intent, not the original underspecified ask
