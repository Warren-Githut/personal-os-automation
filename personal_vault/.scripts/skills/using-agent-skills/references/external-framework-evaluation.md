# External Framework Evaluation — Hermes Ops Pattern

> Documented from: Loop Engineering deep research session (2026-06-30)
> Framework: [cobusgreyling/loop-engineering](https://github.com/cobusgreyling/loop-engineering)

## When to Use

A new framework, tool, paper, or paradigm appears (Loop Engineering, Harness Engineering, Goal Engineering, etc.) and you need to assess:
- Can we use this **directly** (CLI, library, patterns)?
- What **concepts transfer** to Hermes ops context?
- What's the **implementation priority**?
- Is it applicable across **all 3 profiles** or just warren-profile?

## Process

### Step 1: Deep Research

Fetch the primary source + all supporting content in parallel:
- README (full raw)
- Core docs (Quickstart, patterns, primitives, failures, safety)
- Foundational essays/articles (Substack, blog posts)
- CLI tools & their tech stack
- Real examples and starters
- License, stars, community activity

Use `web_extract` for GitHub raw content, `web_extract` for docs, `web_search` for context.

### Step 2: Map to Current Hermes Stack

Evaluate against every layer:

| Layer | Check | Example from Loop Engineering |
|-------|-------|-------------------------------|
| **Profiles** | Applicable to warren / stock / personal? | warren: 🔶 Medium (concepts); stock: 🔴 Low; personal: ⚫ None |
| **Cron jobs** | Any pattern match với cron hiện tại? | Daily Triage → daily-ops-brief; CI Sweeper → col-queue-watcher |
| **Skills** | Skill nào đã cover primitive này? | Scheduling, Sub-agents, State/Memory (Hermes đã có) |
| **Tools** | CLI/package có chạy được Hermes (Python) ko? | npm Node.js tools ❌ — Hermes stack Python |
| **Architecture** | Concept conflict với design hiện tại? | Delegation zones 🟢🟡🟠🔴 map được L1→L2→L3 |
| **Vault** | File structure compatible? | STATE.md = CONTEXT.md/TODAY.md concept |

### Step 3: Extract → Conceptualize

Map framework primitives to Hermes equivalents, identify gaps:

```markdown
| Framework Primitive | Hermes Equivalent | Gap / Extraction |
|--------------------|-------------------|------------------|
| Post-run critique  | Cron chưa có       | → Item B: AUTOMATION_HEALTH.md |
| Cost observability | Hermes chưa track  | → Item A: token tracking |
| Loop Ready score   | audit-automation   | → Item D: expand scoring |
| Failure catalog    | failures rải rác   | → Item C: consolidate |
| Multi-loop coord   | cron conflict risk | → Item E: lock mechanism |
```

### Step 4: Prioritize

Order by effort/value. Present as table:

| Item | Effort | Value | Priority | Note |
|------|--------|-------|----------|------|
| B — Post-run critique | Low | High | 1 | Quick win, continuous improvement |
| A — Cost tracking | Medium | High | 2 | Data-driven decisions |
| C — Failure catalog | Low | Medium | 3 | Builds on B entries |
| D — Loop Ready score | Medium | Medium | 4 | Needs A + B + C foundation |
| E — Multi-loop coord | High | Low-Med | 5 | Research-heavy |

### Step 5: Execute via Lifecycle

Use `using-agent-skills` workflow from interview → implement:

1. `interview-me` — clarify scope + priority + assumptions
2. `idea-refine` — expand concepts, generate variations, converge
3. `spec-driven-development` — write spec, Warren reviews
4. `planning-and-task-breakdown` — breakdown into ordered steps
5. `incremental-implementation` — step-by-step with verification

## Common Pitfalls

| Pitfall | Mitigation |
|---------|------------|
| Assuming framework CLI tools work in Hermes (npm/pipenv mismatch) | Check tech stack first. Python-only for Hermes. |
| Copying patterns verbatim without ops context adaptation | All 7 Loop Engineering patterns were software engineering (PR, CI, changelog). Must adapt for ops (restaurant data, Telegram, GSheets). |
| Forgetting to check all 3 profiles | Framework may fit warren-profile but not stock or personal. Document per profile. |
| "Not applicable" guilt | Valid conclusion. Say so directly. Don't force fit. |
| Over-indexing on tooling, under-indexing on concepts | Concepts > tools. The repo's 4 CLIs were irrelevant; the 5 extracted concepts were valuable. |

## Verification Checklist

- [ ] Read primary source + all supporting docs
- [ ] Mapped against profiles (warren, stock, personal)
- [ ] Mapped against existing cron jobs
- [ ] Mapped against existing skills
- [ ] Extracted framework-agnostic concepts (not tool-dependent)
- [ ] Prioritized by effort/value
- [ ] Executed via using-agent-skills lifecycle (interview → spec → implement)
- [ ] Documented outcome and any lessons for future sessions

---

## Worked Example — Matt Pocock `mattpocock/skills` (2026-07-09)

**Source:** `github.com/mattpocock/skills` (163k⭐, v1.1.0, MIT). Survey post: X `@mattpocockuk/status/2075218406266036236`.

**Discovery method:** X post via `web_extract`; repo + raw SKILL.md files via `web_extract` on `raw.githubusercontent.com/...`; liteparse gate applied to the attached screenshot (it was a repo-page screenshot — liteparse confirmed, no vision needed). `x_search` failed (credits) — fell back to web_extract, sufficient.

**Capability map (external → Warren vault):**

| Matt skill | Warren equivalent | Verdict |
|-----------|-------------------|---------|
| `/to-spec` | `spec-driven-development` | Duplicate ~90% |
| `/to-tickets` | `planning-and-task-breakdown` | Duplicate — "blocking edges" = Warren's `**Dependencies:**` field (already present) |
| `/implement` | `incremental-implementation` | Duplicate |
| `/code-review` | `code-review-and-quality` | Duplicate (Matt runs 2 axes as parallel subagents) |
| `/tdd`, `/diagnosing-bugs` | `test-driven-development`, `debugging-and-error-recovery` | Duplicate 100% |
| `ask-matt` (router) | `using-agent-skills` | Same role |
| `/grill-with-docs` | `interview-me` + `documentation-and-adrs` | Matt folds ADR + domain-model build inline — smoother |
| `/handoff` | **(missing)** | ADD — compact session → handoff doc for next agent |
| `/wayfinder` | **(missing)** | ADD as `/wayfinder-local` — uses `_cases/`, not GitHub |
| `/writing-great-skills` | `ruthless` + `bulk-skill-edit` | Warren has it; lacks "predictability/completion-criterion" framing |

**Key pitfalls confirmed this session:**
- Warren's vault IS code (parsers/scripts) → code-flow skills DO apply. Do not say "not applicable to ops."
- Patch target `planning-and-task-breakdown` was in `common/` (bundled) — must NOT edit; the feature already existed anyway. **Override protocol:** to change a bundled skill, create `C:/Users/khoans/AppData/Local/hermes/profiles/warren-profile/skills/<same-category>/<same-name>/SKILL.md` with the same `name:` field (warren-profile copy wins over bundled). Never patch `...\hermes\skills\common\...` in place.
- "Missing feature" assumption: Matt's "blocking edges" = Warren's `**Dependencies:**` field already in `planning-and-task-breakdown`. Read the full skill body before patching.

**Recommended action shape:** dedup (absorb mechanics, keep Warren Gates) + add only genuine gaps (`/handoff`, `/wayfinder-local`). Do NOT install the bundled `setup-matt-pocock-skills` (Claude Code installer, irrelevant to Hermes).

---

## Worked Example — garrytan/gbrain (2026-07-18)

**Source:** `github.com/garrytan/gbrain` (26.5k⭐, MIT). YC president Garry Tan's "agent brain" — typed knowledge graph + synthesis layer + 24/7 nightly consolidation. Built on Postgres/pgvector (PGLite WASM), Bun, MCP, commercial embeddings (ZeroEntropy/Voyage).

**Discovery method:** `web_extract` on repo README + `docs/ethos/ORIGIN.md` + `docs/what-schemas-unlock.md` + `AGENTS.md` (raw.githubusercontent). Same path as Loop/Matt — GitHub raw via web_extract, never rely on web_search alone.

**Deep-research verdict (Warren asked "áp dụng được ko, tốt hơn memory warren không"):**
- gbrain solves 2 problems Garry hit: (1) agent forgetting between sessions (flat markdown + ripgrep), (2) duplicate work (no graph). → **Warren already solved both** via vault-first + session bootstrap (SOUL§6/session-start HARD GATE) + SSOT discipline + WARREN_MEMORY.md. NOT a gap.
- gbrain wins on exactly 2 things: (a) typed graph traversal ("who works at X"), (b) 24/7 auto-consolidation (dedup/contradiction detection). BUT both need Bun/Postgres/MCP/OAuth + token cost → **conflicts hard with Warren's "non-IT", "ALL CRONS = FREE ONLY", "vault file readable" rules.**
- gbrain optimized for personal-network brain (people/companies/deals) — Warren is F&B ops. Default schema (gbrain-base 22 types) has NO ops types → would need full ontology re-authoring. Overkill at Warren's scale (dozens–few-hundred files vs gbrain's 100K).

**Decision framework that emerged (reuse for any "should we adopt X" question):**
| Option | When to pick |
|--------|--------------|
| A. Skip entirely | Framework solves a problem you don't have |
| B. Partial borrow (concepts only) | Framework's *idea* is valuable but its *stack* conflicts with your constraints → reimplement the idea on your existing stack |
| C. Pilot on subtree | Genuine uncertainty, low blast radius |
| D. Full migrate | Only if current stack is actually failing |

→ Warren chose **B**: borrowed gbrain's "24/7 auto-consolidation" as a 0-token nightly cron (`vault_consistency_nightly.py`) scanning SSOT conflicts / orphans / gaps, delivering Telegram + `CONSISTENCY_LOG.md`. No migration, no DB, no token.

**CRITICAL lesson captured this session (embed in skill, not just memory):**
> When evaluating an external brain/memory tool, the agent's OWN claims about its current memory stack are UNTRUSTED. Warren's WARREN_MEMORY.md *asserted* "warren uses mem0 FAISS" — on-disk verification showed warren-profile has NO mem0.json / mem0_faiss/, config `mem0:` block empty, only built-in `memory` tool exists. The claim was a 2026-07-09 hallucination that survived 9 days. **Verify the agent's memory infrastructure on disk (find/ls/grep) before citing it in any comparison.** This generalizes: never trust a memory-file claim about tooling state — check the filesystem.

**fit-against-Warren-rules gate (add to Step 2 mapping):** When a framework needs infra (DB/server/token/non-IT-unfriendly), score it 🔴 if it collides with any HARD rule: non-IT user, ALL CRONS FREE ONLY, vault-readable-not-blackbox, simplify/SSOT. gbrain hit 3 of 4 → auto 🔴 on adoption, 🟢 only on concept-borrow.

**Verification checklist addition:** after deep-research, before recommending adopt — run `find`/`grep` on disk to confirm the agent's *current* stack matches what memory files claim. Mismatch = flag + correct the memory file.
