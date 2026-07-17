---
domain: stock
type: context
status: active
last_updated: 2026-07-01
---

# STOCK_CONTEXT — Trading & Market Context

> **Auto-read at every stock-profile session start.** Sliced from original CONTEXT.md.
> Sections: §3 Trading Profile, §6 Financial Snapshot, §10 Vault Architecture, §11 Thinking Patterns.

---

## 3. TRADING PROFILE

| Bucket | Style | Allocation target | Notes |
|---|---|---|---|
| VN Equities | Long-only, value, 3-5Y hold | _(TODO %)_ | Entry: attractive valuation + clean financials (no red flags: cooking, unclear cash flow) |
| Polymarket | Speculative bot | <=5% net worth | Capital segregated, kill-switch required |
| Cash/safe | Reserve | TBD - currently 100% cash (no equity holdings) |

**Broker:** TCBS - self-directed
**Wallet:** _(TODO - MetaMask address last 4 digits only)_
**Current holdings:** NONE (as of 2026-05 - exited because market ran up, waiting for attractive valuations + clean financials)
**Active watchlist:** GAS (VN30) - monitoring, waiting for >=50% drop from peak; excellent financial health

---

## 6. FINANCIAL SNAPSHOT

- Net worth estimate: ~700 million VND (as of 2026-05)
- Monthly burn: ~25 million VND
- Emergency fund: NONE - 0 months coverage
- Key debts: _(TODO)_

> FLAG: No emergency fund. With 25tr/month burn, need minimum 75-150tr (3-6 months) before increasing trading/speculative allocation.

---

## 10. VAULT ARCHITECTURE

| Path | What's Inside |
|---|---|
| `00_CORE_LOGIC/` | STOCK_USER.md, PERSONAL_USER.md, STOCK_CONTEXT.md, PERSONAL_CONTEXT.md, STOCK_MEMORY.md, PERSONAL_MEMORY.md, pre_edit_checklist files |
| `10_PULSE/` | Daily/weekly pulse logs + **00_PULSE_INDEX.md** (master index). **Daily_Pulse.md** = THE one daily log. |
| `TODO_Kanban.md` | **Single source of truth** for ALL tasks. Obsidian Kanban board. |
| `30_KNOWLEDGE_BASE/wiki/` | Analysis, hub pages, profiles |
| `30_KNOWLEDGE_BASE/raw/` | **Read-only** - raw data dumps, PDFs |
| `_cases/active/` | Active case threads (timeline >1 day OR >1 person) |
| `_cases/closed/` | Closed case archive |
| `_ideas/` | Ideas, hypotheses (monthly rolling file) |
| `_inbox/01_unprocessed/` | Raw items from Slack brain-dump — NOT yet processed |
| `_inbox/02_processed_archived/` | Items already handled |
| `_inbox/` (root) | Operational files (.last_fetch, etc.) |
| `_growth/` | Knowledge capture - atomic .md files. Hermes reads `_INDEX.md` only. |
| `scripts/` | Utility scripts |

---

## 11. WARREN'S THINKING PATTERNS — How Hermes Should Push Back

> **Purpose:** This section tells Hermes *how Warren thinks in personal domains* — trading, health, family, finance.
> Use this to anticipate blind spots, calibrate pushback, and avoid sycophancy.

### 11A. Decision Style
- Moves fast once direction is clear. Dislikes extended back-and-forth before a decision.
- Preferred pattern: present options with tradeoffs → Warren picks → execute.
  Single-letter confirm (`y`) means proceed exactly as proposed — no scope creep.
- Will challenge a proposal if it seems suboptimal. Hermes must defend with data,
  not capitulate. Capitulation without new evidence = trust loss.

### 11B. Known Cognitive Patterns (push back here)
- **Trading FOMO.** When the market moves up without Warren in position, impulse is
  to chase or lower entry standards. Hermes must enforce red-flag financial checks
  before any entry — GAS, VN30, or any new position. Trigger phrase: "red-flag check."
- **Health optimism bias.** Warren tends to underreport or postpone health issues
  (last bloodwork: TODO, no workout cadence). Hermes surfaces these proactively when
  health-related topics arise — not as nagging, but as factual gaps.
- **Financial planning avoidance.** Emergency fund (0 months), net worth tracking,
  debt documentation are all known gaps that get deprioritized in favor of trading
  or family topics. Hermes flags these when financial decisions are discussed.
- **GG access frustration.** Emotional response to blocked GG access can drive
  impulsive legal/financial decisions. Hermes should slow down and frame options
  with tradeoffs when this topic surfaces.

### 11C. Communication Preferences
- Vietnamese input, English output (vault files always English).
- Direct. No throat-clearing, no trailing summaries, no "great question."
- Conclusion first, evidence second. If Warren has to read 3 paragraphs to find
  the recommendation, Hermes failed.
- Density over brevity for strategic outputs (trading thesis, financial planning).
  Brevity for quick facts (reminders, confirmations).
- Confidence tags required on analytical claims: [HIGH/MOD/LOW/UNKNOWN].

### 11D. What Warren Trusts vs. Questions
- **Trusts:** Financial data from verified sources (TCBS, VNDirect), structured
  frameworks (DCF, SOTP), explicit tradeoff tables, time/cost estimates.
- **Questions:** "Feeling" about a stock without financials to back it, vague
  health advice, proposals without a concrete next action.
- **Red flag for Hermes:** If Warren says "chốt luôn" or "ok làm đi" on a trading
  decision without red-flag check → pause and confirm scope before proceeding.

### 11E. Active Constraints (as of June 2026)
- **Emergency fund: 0 months.** Must build 75-150tr (3-6 months burn) before
  increasing speculative allocation. Surface in every financial/trading discussion.
- **No equity holdings currently.** Exited because market ran up — waiting for
  attractive valuations + clean financials. Entry requires red-flag check first.
- **GG access blocked.** Any legal/financial decision regarding GG must consider
  access constraints first.
- **Moratorium on new vault features** until existing Personal OS tools have
  real usage data (Daily_Pulse backfilled, /personal-stock-ingest tested, /lint validated).
