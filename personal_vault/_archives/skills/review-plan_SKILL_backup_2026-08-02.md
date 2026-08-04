---
name: review-plan
description: Adversarial review for data/vault plans.
category: devops
tags: ['review', 'plan', 'adversarial', 'data']
version: 1.0.0
trigger: /review-plan [plan]
related_skills: [review-audit]
---

# /review-plan
Review plans with adversarial personas.

## Phases
1. Read and frame
2. 4-persona debate using vault history
3. Cross-examination
4. Senior manager verdict
5. Spec block output
6. Auto-implement on approval

## Auto-route
- Small plans -> lightweight verdict only
- Code-heavy -> redirect to `review-audit`
- Contradicts history -> critical blocker

## Ops-Pipeline Integration
For structural vault changes (new schema, parser restructuring, index redesign), this skill integrates with `/generate-plan`:
1. `/generate-plan <requirement>` — produces structured spec with phases, files, risk
2. `/review-plan <plan>` — adversarial 4-persona review → verdict → spec block
3. **Auto-implement on approval** — the spec block from step 2 is the final contract

This workflow was used in the 2026-06-19 universal frontmatter schema rollout across all 15 `10_OPERATION_DATA/` files. The review-approve gate caught schema_version as premature (removed from scope) and trimmed last_reviewed to static files only, saving ~20 field additions that would have been dead code.

---

### 3. Operational File Completeness Audit

> **Class:** Review existing wiki/analysis/tracker files for decision-readiness and Warren-actionability.
> **Trigger:** Warren gửi file path + yêu cầu review (e.g. "bạn là FBM 30 năm, hãy xem file này").
> **Differs from Plan Review (Phase 1):** This audits *existing* content — not proposed plans. Single authoritative voice (role-played), no 4-persona debate. Deliverable: scored gaps + format rewrite.

#### Framework — 7 Dimensions

| # | Dimension | Check | Example question |
|---|-----------|-------|-----------------|
| 1 | **Profitability depth** | Has margin data beyond top-line? (COGS, food cost) | "Net payout X but cost structure?" |
| 2 | **Product mix** | Best sellers, category split, items/order? | "Top 5 items on channel?" |
| 3 | **Operational logistics** | Prep time, cancellations, ratings, peak hours? | "Why is rating 2★?" |
| 4 | **Competitive context** | Ranking position, competitor activity? | "Where do we rank on Grab?" |
| 5 | **Store coverage** | All stores included? Status current? | "LU7 blocked by mall policy?" |
| 6 | **Data recency** | Last update? Newer data available? | "June missing, only May" |
| 7 | **Format & readability** | M format? % WoW? Conclusion-first? | "VND numbers too long" |

#### Scoring Template

```
| Tiêu chí | /10 | Ghi chú |
|----------|:---:|---------|
| Hermes grep-able/searchable | 7/10 | ... |
| Hermes phân tích/actionable | 5/10 | ... |
| Warren nhìn hiểu ngay | 7/10 | ... |
| Dễ ra quyết định | 5/10 | ... |
```

#### Format Improvement Pattern (Warren-approved)

- **Long VND → M/k format** — `45,075,840 VND` → `45.1M`
- **% WoW column** in weekly tables
- **Vietnamese with diacritics** for narrative (headers stay English: "Gross GMV")
- **Confidence tags** `[HIGH]`/`[MOD]`/`[UNKNOWN]` on every insight
- **Conclusion-first** exec summary, zero preamble
- **Specific actions** — budget, store, hours — not "resume ads" alone
- **Data citation** — every number cites source path

#### Pitfalls — What Warren Will Reject

| Over-request | Response | Lesson |
|--------------|----------|--------|
| Deep food cost analysis | "Chưa cần" | Use existing vault data; don't demand new |
| Delivery ops metrics | "Ignore" | Skip unless Warren asks |
| Competitive context | "Để trống" | Flag gap, don't block |
| Suggesting new data sources | "Tôi sẽ gửi" | He provides; note gaps only |
| Asking about initiatives | "Đã làm rồi" | Check recent files first |

#### Data Integration Pattern (CSV/Excel attachment)

1. Parse → categorize (food/drinks/sides), top-N ranking per store
2. Add as new section (e.g. "Best Seller — 90 Ngày")
3. Include category mix %, top items, AOV per item
4. Cross-reference with ad/revenue strategy — which items to push

#### Example
See `references/2026-07-04_grabfood-tracker-audit.md` for full session trace.

---

## System & Security Audit (from `review-audit`, merged 2026-07-22)

> Umbrella: code review, system audit, security triage, and external-tool evaluation. All produce **structured findings** with priority/effort/impact — Warren conclusion-first, non-IT.

### Domains
**1. Code Review & Cross-Reference Audit** — Review single-file quality, multi-file references, parser output format, frontmatter integrity, index sync.
- **Checklist:** Version tag in code matches frontmatter · All expected output sections present · Index synced · No stale cache artifacts · Historical output unchanged (grep regression).
- **Parser output constraints:** vault markdown rules (em dashes, diacritics, pipe counts, JSON shape, number formatting) → `references/parser-output-constraints.md`.

**1b. Parallel fan-out review** — Khi cần review 1 artifact bằng nhiều lens (battle-test / ab-test / debugging / code-review / code-simplification) → fan-out N subagents song song (delegate_task), mỗi ông load 1 skill + review read-only. Gộp findings ở parent. Subagent KHÔNG write_file/patch (zone 🟢). Warren review → chốt. Edit thực tế = zone 🔴.

**2. Security Audit Triad** — gitleaks + bandit + pip-audit (parallel):
| Tool | What | Install | Run |
|------|------|---------|-----|
| **gitleaks** | Credential leaks | `winget install gitleaks` | `gitleaks detect --report-path /tmp/gl.json` |
| **bandit** | Python security lint | `pip install bandit` | `bandit -r vault/scripts/ -f json -o /tmp/bandit.json` |
| **pip-audit** | Known CVEs | `pip install pip-audit` | `pip-audit` |

**Credential Leak Response:** (1) Add to `.gitignore` → (2) `git rm --cached <file>` (keeps disk) → (3) commit+push. KHÔNG `git rm` (mất file). Verify: re-run gitleaks → 0 leaks in HEAD.

**3. External Tool Evaluation** — 4-quadrant: Workflow fit / Codebase fit / Cost-benefit / Infra compatibility. Output: ✅ Fit / ❌ Skip / 🟡 Marginal + evidence.

### Output format — 4-tier priority
```
🔴 CRITICAL — fix ngay (credential leak in HEAD)
🟡 MEDIUM — cần action (known vulns, deprecated patterns, leaks in history)
🟢 LOW — optional (false positives, cosmetic)
⚪ NOISE — skip
```
Each finding: `| Priority | What | File:line | Why | Fix command |`
