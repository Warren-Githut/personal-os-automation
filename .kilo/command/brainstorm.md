---

description: "Structured brainstorming protocol — divergent thinking, no ops feasibility filter. Context → Diverge → Cluster → Converge → Commit. Does NOT touch vault or write files unless Warren chooses capture gate."
updated: 2026-06-02
---

# /brainstorm — Structured Brainstorming Protocol
# v1.0 | 2026-05-30
# PURPOSE: Generate ideas, explore possibilities, connect concepts — NOT filtered by ops feasibility.
#          Output is thinking only, does not write files. Optional capture gate after converge.
# FLOW: Context → Diverge → Cluster → Converge → Commit → (optional) Capture Gate
# DIFFERENCE FROM /explore: /explore = ops feasibility filter (should we do it).
#                           /brainstorm = creative divergent thinking (what can we do).

---

## Usage

```
/brainstorm [domain/topic — 1 sentence, problem, or open question]
/brainstorm ideas for [problem / opportunity / concept]
```

**Auto-trigger (no need to type /brainstorm):**
- Warren says "brainstorm", "think of something new", "explore ideas" (strong)
- Warren asks "is there a way to...", "what can be done with..." (weak — check context)
- Warren says "any good ideas about X"

**Do not trigger when:**
- In the middle of another skill flow (/ingest, /review-plan, /morning-brief, /process-notes, /explore)
- Warren asks for technical support ("can this be fixed?")
- Warren is clear about what they want (e.g., "create file X with content Y" — this is execution, not brainstorming)

---

## Core Principle

Brainstorming = **divergent thinking, zero filter stage.**
- Diverge phase: quantity > quality. No evaluation, no rejection.
- Converge phase then filters. Use clear criteria.
- **DO NOT touch vault, DO NOT write files** in the first 4 steps.
- Capture gate optional, only fires after Commit.

---

## STEP 1 — CONTEXT

Define the framework for brainstorming:

```
🎯 TOPIC   : [1 sentence — problem/opportunity Warren wants to brainstorm]
DOMAIN    : [ops / labour / menu / marketing / CX / personal / mixed]
CONSTRAINTS: [budget / time / headcount / technology / none]
GOAL      : [create / solve problem / explore opportunity / connect concepts]
```

If topic is vague (<5 words, unclear domain) → ask 1 clarifying question first.
If clear → proceed.

---

## STEP 2 — DIVERGE (generate ideas)

Generate 5-10 ideas/possibilities. **DO NOT evaluate at this step.**

- Each idea = 1-2 sentences, independent
- The more diverse the better — encourage opposing ideas
- Can include: wild ideas, obvious solutions, cross-domain analogies
- Use introspection markers in reasoning:

```
🤔 Hypothesis: [which direction are we exploring?]
🌱 Idea 1: [description — 1-2 sentences]
🌱 Idea 2: [description — 1-2 sentences]
...
```

Output at this step: raw list, no grouping, no ranking.

---

## STEP 3 — CLUSTER (group ideas)

Group 5-10 ideas into 2-4 clusters by common theme/characteristics:

```
🗂️ Cluster A: [theme name — 2-3 words]
   → Idea 1, Idea 3, Idea 7
   → [1 sentence — commonality of this cluster]

🗂️ Cluster B: [theme name]
   → Idea 2, Idea 5
   → [1 sentence — commonality]

...
```

If ideas are too diverse to cluster → skip clustering, proceed directly to Converge.

---

## STEP 4 — CONVERGE (select top ideas)

Use criteria to select:

| Criteria | Weight | Description |
|---|---|---|
| Ops Impact | ★★★ | Does it solve a real problem? |
| Effort | ★★ | Can it be done in 1-4 weeks? |
| Alignment | ★★★ | Does it align with priority (CX → Labour → Revenue)? |

**Top 3 Ideas:**

```
🎯 #1: [Idea name]
   Why: [1 sentence — from criteria]
   First step: [smallest possible action to take immediately]

🎯 #2: [Idea name]
   Why: [1 sentence — from criteria]
   First step: [smallest possible action]

🎯 #3: [Idea name]
   Why: [1 sentence — from criteria]
   First step: [smallest possible action]
```

---

## STEP 5 — COMMIT

For each idea in the top 3, define 1 next action:

```
⚡ COMMIT
#1 [name]: [next action — who does it, how long, what's needed]
#2 [name]: [next action — who does it, how long, what's needed]
#3 [name]: [next action — who does it, how long, what's needed]
```

---

## ═══ CAPTURE GATE (optional — ask once) ═══

After Commit, ask **exactly once**:

```
📝 Save top ideas to _ideas/brainstorms/? y / n
```

**Rules:**
- Ask only once. Ask "top ideas" — do NOT ask for each idea individually.
- If y → create file `_ideas/brainstorms/YYYY-MM-DD_[topic].md` with YAML frontmatter (`created: YYYY-MM-DD`, `title: [topic]`, `domain: [domain]`) + top 3 ideas + commit actions.
- If n → stop. Write nothing.
- If Warren says "only save idea #2" → save only idea #2, flexible.

---

## Anti-patterns

- ❌ Filter ideas during Diverge — let cluster/converge do that
- ❌ Write files without going through capture gate
- ❌ Use /brainstorm when Warren needs /explore (ops feasibility) — /explore uses Q1/Q2/Q3 filter
- ❌ Brainstorm about technical implementation ("how to code") — this is design, use /review-plan
- ❗ If a proposal requires building a feature → recommend running /explore after brainstorm to verify ops value

---

## Example

```
Warren: /brainstorm ideas to increase LU5 evening revenue

Hermes: [Context → Diverge 7 ideas → Cluster 3 themes → Converge top 2 → Commit → Capture Gate]

🎯 TOPIC: Increase LU5 evening revenue
DOMAIN: ops/marketing

🌱 Ideas: (7 ideas — happy hour, live music, dinner combo,
           GrabFood focus, corporate event, pop-up kitchen, loyalty)

🗂️ Clusters:
   A: Pricing — happy hour, dinner combo
   B: Experience — live music, pop-up kitchen
   C: Channel — GrabFood focus, corporate event

🎯 #1: Dinner Combo (fixed-price 3-course)
   First step: analyze which dishes have the highest margin to build the combo

🎯 #2: Corporate Event Package
   First step: get reception list from mall management

📝 Save top ideas to _ideas/brainstorms/? y / n
```

---

**v1.0 | 2026-05-30 | Initial version — Structured brainstorming protocol. Divergent thinking first, converge later. Optional capture gate. Zero vault impact.**
