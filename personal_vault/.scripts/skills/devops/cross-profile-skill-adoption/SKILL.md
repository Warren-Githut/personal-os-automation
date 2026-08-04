---
name: cross-profile-skill-adoption
description: "Adapt a Hermes skill (or skill trio like auto-reviewer + reviewer-node + safenet) from one profile to another profile. Encodes the adapt-don't-copy discipline: rewrite domain-specific references (ANCHORS path, checklist content, routed skill names) instead of copying verbatim. Use when Warren says 'adopt this to stock-profile / personal-profile'."
version: 1.0.0
author: Hermes
category: devops
related_skills: [subagent-pattern, skill-lifecycle, auto-reviewer, reviewer-node, safenet]
---

# Cross-Profile Skill Adoption

> Warren runs 3 Hermes profiles (warren-profile, stock-profile, personal_profile). A proven skill often needs to exist in all three — but **copying verbatim corrupts it**. This skill is the discipline for adapting.

## The 38/100 lesson (why this exists)

stock-profile once held a verbatim copy of warren's review-gate (auto-reviewer + reviewer-node + safenet). Battle-test scored it **38/100**: the structure was fine (token, HARD BLOCK) but **0% domain adaptation** — the checklist referenced `LU3/LU5/LU7` colors, `A1 LU7 10h mall regulation`, `revenue M (triệu VND)`, and loaded `vault/00_CORE_LOGIC/ANCHORS.md` (a warren-only path that didn't exist in stock). Every stock review was corrupted (false-flag or rubber-stamp).

**Rule: copy structure, adapt domain.**

## What to KEEP identical (structure)

- Separate reviewer node via `delegate_task` with CLEAN context (no Hermes raw data/transcript).
- Free-model inheritance — **NO hardcoded model** in any frontmatter (Warren directive: all crons/agents on free models).
- Exact mandatory deliver token format (e.g. `🔍 REVIEWER:` orchestrator-only).
- HARD BLOCK on FAIL#2 (artifact not delivered without explicit override).
- Context-clean rule (only {artifact}+{checklist}+{anchors_summary}).

## What to ADAPT per profile (domain)

| Element | Warren (L'Usine F&B) | Stock (investing) | Personal (health/family) |
|---|---|---|---|
| ANCHORS path | `Warren_OS_Local/vault/00_CORE_LOGIC/ANCHORS.md` | `Stock_OS/stock_vault/00_CORE_LOGIC/ANCHORS.md` | (create per personal vault) |
| Checklist 5 axes | revenue/covers/LU3-7/Rev-per-Cover/Labour% | P/E, EPS, thesis, risk, capital segregation, ≥4 quý | sleep/health/finance/logic |
| Routed skills | verify-data-window (L'Usine) | remove; use inline A7 ≥4 quý rule | per personal domain |
| Hard rules cited | A1 LU7 10h, A2 SSOT | A1 thesis, A2 risk, A4 capital, A5 conviction, A7 data-window | personal ANCHORS |

**Concrete steps:**
1. Locate the target profile's real vault/ANCHORS path (don't assume `vault/00_CORE_LOGIC/` — stock uses `Stock_OS/stock_vault/00_CORE_LOGIC/`). Use `terminal` `ls`/`find` (bounded) to confirm, not guess.
2. Create/confirm `ANCHORS.md` in target profile with that profile's frozen rules.
3. Rewrite the checklist axes to the target domain (see references/stock-adaptation-case.md for the stock rewrite).
4. Rewrite auto-reviewer's `read_file` ANCHORS path to the target's real path (both in How-to-call and Pitfalls).
5. In safenet routing table: replace any source-profile-specific routed skill (e.g. `verify-data-window` is L'Usine-only) with a target-appropriate gate or inline rule.
6. Change the skill `description` frontmatter `warren-profile` → `<target>-profile`.
7. **Propagate forced-critic override (2026-07-22 lesson):** Nếu source-profile có Warren override "mọi analysis/report kể cả zone 🟢 → FORCED spawn reviewer-node" (safenet §D Warren override), target-profile PHẢI có tương đương — KHÔNG để target giữ "high-stakes only" mù quáng. Adapt scope theo domain risk:
   - **stock:** high-stakes + mọi research note / eval / buy-sell-hold call (đã có qua auto-reviewer, confirm forced).
   - **personal:** analysis có số đáng kể (sleep/finance/health metric) → forced; chat thường → skip.
   - Đừng copy blind "kể cả 🟢" — personal ít rủi ro hơn warren, scope hẹp hơn là hợp lý. NHƯNG không được quay về "chỉ high-stakes" nếu source đã forced mọi analysis.
   - **⚠️ SYMLINK SHORT-CUT (2026-07-22):** Vì `stock-profile/skills` + `personal_profile/skills` là symlink → `warren-profile/skills`, nên **patch safenet/reviewer-node 1 lần trong warren-profile là CẢ 3 profile có chung file**. KHÔNG patch skill riêng stock/personal (cross_profile guard sẽ block hoặc lãng phí). Chỉ việc: (a) patch warren `skills/core/safenet` + `reviewer-node` 1 lần, (b) add SOUL.md note riêng cho stock + personal (personal SOUL nằm ở AppData personal_profile, không có vault SOUL.md local). Verify bằng `grep -c "FORCED for ALL profiles" <profile>/skills/core/safenet/SKILL.md` = 1 cho cả 3.

## Cross-profile write gate (HARD)

Writing to another profile's `skills/` requires explicit Warren approval. Once approved:
- Pass `cross_profile=True` to `skill_manage` (patch/create/write_file) and `patch` tool.
- The cross-profile soft guard refuses by default — approval is the only bypass.

## Verification (mandatory before push)

1. **Drift grep** on the adapted files — must return ZERO hits for source-domain tokens:
   ```
   grep -rn "LU3\|LU5\|LU7\|triệu VND\|Saigon Centre\|mall regulation\|warren-profile\|<old ANCHORS path>\|<source-specific skill>" <target>/skills/...
   ```
2. **Re-run battle-test** subagent on the target profile → confirm **≥85/100** (structural PASS + domain fit). If <85, more adaptation needed.
3. Backup adapted skills to target vault `_archives/skills/` (SOUL §5 Archive Gate) then commit/push with Commit-Push Self-Gate.

## Pitfalls

- **Verbatim copy** → 38/100 corruption. Always adapt (cho hard-copy case).
- **Wrong ANCHORS path** → reviewer loads nothing / loads wrong profile's rules. Confirm path on disk first.
- **Leaving source-domain checklist** → reviewer flags nonsense (e.g. "LU7 10h" in a stock note).
- **Referencing source-only skills** (verify-data-window is L'Usine) → dead route or wrong-domain gate.
- **Symlink reality check (2026-07-22 — OVERRIDES old "symlink assumption" pitfall):** Trên máy Warren, `stock-profile/skills` và `personal_profile/skills` là **symlink trỏ thẳng sang `warren-profile/skills`** — xác nhận bằng `ls -la <profile>/skills` → `lrwxrwxrwx ... skills -> /c/Users/.../warren-profile/skills`. Hậu quả: patch skill 1 lần trong warren-profile = **cả 3 profile dùng chung file**, KHÔNG cần adapt/duplicate structural change (safenet/reviewer-node). Chỉ patch **SOUL.md riêng từng profile** (tracked, domain note). → Quy trình đúng: (1) `ls -la <profile>/skills` confirm symlink vs hard-copy; (2) symlink → patch warren 1 lần + add SOUL.md note mỗi profile; (3) hard-copy → áp dụng adapt discipline cũ. Đừng mù quáng "adapt" khi thực ra shared.
- **personal_profile KHÔNG phải git repo (2026-07-22):** `git rev-parse` báo "not a git repository". Skill patch vẫn lưu disk (shared symlink → effective) nhưng không commit/push được. Báo Warren nếu muốn `git init`.
- **Profile-repo commit hygiene (2026-07-22):** `.gitignore` ignore `skills/` → skill patch KHÔNG vào git; NHƯNG state files (gateway.pid, cron/jobs.json, pending/memory/*.json x60, state/gateway.heartbeat, .skills_prompt_snapshot.json) KHÔNG ignore → `git add -A` cuốn rác. Fix: `git reset` (mixed) + chỉ `git add SOUL.md` (file đáng commit). Xem `git-workflow-and-versioning` (nếu được phép sửa) hoặc áp dụng pattern này.
- **Git remote map per profile (2026-07-22 — TRÁNH lãng phí push fail):** Đừng mù quáng `git push` mọi profile. Thực tế:
  - `vault Warren_OS_Local` → remote **ĐÃ BỐ XÓA** (repo 404) → push FAIL, commit local thôi. Backup `_archives/skills/` cũng không push được.
  - `warren-profile` (AppData) → git repo NHƯNG remote trỏ vault repo đã xóa → **KHÔNG có remote hợp lệ**, local commit only, NEVER push.
  - `stock-profile` (AppData) → remote `https://github.com/Warren-Githut/stock-profile.git` → **push OK**.
  - `personal_vault` (`Documents/Personal_OS/personal_vault`) → remote `https://github.com/Warren-Githut/personal-os-automation.git` → **push OK** (Bố hay gọi nhầm là `personal-os-vault`). `personal_profile` (AppData) KHÔNG phải git repo.
  → Quy trình push đúng: chỉ push **stock-profile** + **personal_vault**. Warren + vault = local-only. Chi tiết + recipe xem `references/git-remote-map.md`.

## References

- `references/stock-adaptation-case.md` — the actual warren→stock adaptation: ANCHORS content, checklist rewrite, drift grep, battle-test 38→92 journey.
- `references/git-remote-map.md` — per-profile git remote reality (vault deleted, warren no-remote, stock/personal_vault push OK) + push recipe + gotchas. ĐỌC TRƯỚC KHI commit/push cross-profile.
