# SOUL.md / Agent Personality Interview Pattern

## When to Use

When the user asks to create or update a SOUL.md (agent personality) file — either for a new Hermes profile or to overhaul an existing one. This pattern extends the base `interview-me` skill with SOUL-specific pitfalls and structure.

## Distinctive Challenges

SOUL.md interviews differ from general feature interviews in three ways:

1. **Aspirational feature injection** — users write what they WISH the agent could do into the personality (push triggers, automated monitoring, scheduled scans). These require capabilities (cron, monitoring loops, live data feeds) that SOUL.md alone can't grant. You must flag these as capability gaps and redirect to what's achievable.
2. **Fake-fillable templates** — users love templates with metrics (IRR, intrinsic value, margin of safety). If the agent can't realistically compute those numbers, the template becomes a lie generator. Every template field must pass: *"Can I actually produce this number from available tools?"*
3. **Personality vs. capability confusion** — users conflate "who the agent is" (tone, identity, values) with "what the agent can do" (tools, integrations, data sources). The former belongs in SOUL.md; the latter belongs in config/skills/AGENTS.md.

## Interview Sequence (add to base interview-me process)

### Phase A: Identity (&rarr; SOUL.md)

Start here. Establish who the agent is before what it does.

| Question | Why |
|----------|-----|
| "Who is this agent — what role do they play for you?" | Establishes identity anchor |
| "What's the communication style? Friendly, cold, technical?" | Tone baseline |
| "What language — English, Vietnamese, mixed?" | Language rule |
| "Conventions: response length? Templates? Conclusion-first?" | Output shape |

**Pitfall:** Users will answer in best-practice speak ("professional," "balanced"). Probe: *"If you didn't have to sound professional, what would you actually say?"* Warren answered: *"Blunt to the point of rude. Ass-kissing free zone."*

### Phase B: Rules & Data Contract (&rarr; SOUL.md)

Non-negotiable constraints. This is where the agent draws lines.

| Question | Why |
|----------|-----|
| "What should the agent never do?" | Hard boundaries |
| "How do you define confidence levels — HIGH, MOD, LOW?" | Quality tags need concrete source definitions |
| "What data is required before the agent can opine on a ticker?" | Integrity gate preconditions |

**Pitfall: Empty confidence tags.** `[HIGH/MOD/LOW]` without source definitions is meaningless. Must define:
```
[HIGH] = audited BCTC / user-provided verified doc
[MOD]  = unverified report, web search, broker report
[LOW]  = estimate, training knowledge, inference
```

**Pitfall: Integrity gate without data precondition.** If the agent must audit BCTC before an entry recommendation, but the user hasn't provided a BCTC file, the agent should auto-respond with `WAIT: need BCTC` rather than guessing. Encode this as a DATA_CONTRACT.

### Phase C: Reality Check on Aspirational Features

This is the highest-value phase. Users will propose features that sound good but don't work.

**Common aspirational features to kill:**
- **Push triggers** ("alert me when X happens") — Hermes is reactive. Push needs cron + a monitoring script. If the user wants it, build it as a cron job, not SOUL.md personality.
- **Automated portfolio rebalancing suggestions** — requires live price feed + position data. If the agent lacks API access, flag it.
- **IRR / intrinsic value calculations** — requires DCF model assumptions. Without a consistent model, these numbers are fabricated.

**Redirect pattern:**
> *"You said [aspirational feature]. That needs [X capability] which SOUL.md can't provide. Here's what we CAN do instead: [realistic alternative]. Want to go that route, or drop it entirely?"*

### Phase D: Template Design (&rarr; SOUL.md)

If the user wants output templates (portfolios, dashboards, stock analyses):

1. **List every field** in the proposed template
2. **For each field, ask:** "Can this agent produce this number, given its current tools and data sources?"
3. **If no** → replace with a qualitative proxy or mark as `[fillable only when data available]`
4. **If yes** → confirm the exact source/method

**Example:** Warren proposed `IRR est. X%` and `margin of safety Y%`. Neither is computable from available data. Replaced with:
- `P/E vs 5Y avg` (computable from web search)
- `Catalyst qualitative` (reasoning-based, no fabrication)

### Phase E: Draft → Critique → Refine → Write

After the restate is confirmed:

1. **Draft** full SOUL.md
2. **Explicitly invite critique** — the user WILL find issues you didn't
3. **Refine** based on feedback
4. **Final language decision** — confirm target language (English / Vietnamese / mixed) before writing
5. **Write to file** — `~/.hermes/profiles/<profile>/SOUL.md` or `$HERMES_HOME/SOUL.md`

## Anti-Patterns Unique to SOUL.md Interviews

| Anti-pattern | Fix |
|---|---|
| User embeds push triggers in personality | Flag: "This needs capabilities, not personality. Remove or make cron job." |
| User wants fancy metrics agent can't produce | Replace with qualitative proxy or remove. Never fabricate. |
| Confidence tags without source definitions | Define concretely: HIGH = audited doc, MOD = web search, LOW = estimate |
| Integrity gate without data precondition | DATA_CONTRACT: gate runs only when source data is present; otherwise auto-CHỜ |
| User says "just make it like Hermes" (default personality) | Interview anyway — the default is generic. You need specific. |
| Template with >5 fields per section | Max 5 bullets (Warren rule: dễ quên chi tiết, cần ít để ra quyết định) |