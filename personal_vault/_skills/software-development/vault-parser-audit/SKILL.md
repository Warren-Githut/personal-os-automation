---
name: vault-parser-audit
description: "Audit, review, and optimize vault parser pipelines: read all parser files, map source/output/formatting, surface duplication and inconsistency, and propose or apply safe refactors."
---

# Vault Parser Audit

Use this skill whenever the user asks to inspect, review, or optimize a set of parsers or automation scripts inside a vault, knowledge base, or operations repo.

## Workflow

1. Inventory parsers
   - List files in the target parser directory.
   - Exclude cache/archives unless the user asks otherwise.
   - Return a compact map: file → source tab/file → output log.

2. Read each parser fully
   - Read every non-cache parser file completely.
   - Record: fetch method, input format, output format, caller prompts, thresholds, stores/locations supported, and inserted metadata.

3. Cross-check for duplication and drift
   - GSheet/data fetch helpers: duplicated `urllib` + gviz/regex blocks?
   - Config: duplicated thresholds, segment maps, store maps, benchmark tuples?
   - Week/period detection: multiple `detect_week()` implementations?
   - Output structure: frontmatter, duplicate checks, newest-on-top, machine-readable blocks?
   - CLI behavior: direct `input()` vs shared prompt helper, headless support.
   - Telegram/notify plumbing: duplicated token readers, `send_telegram()` wrappers, hardcoded `CHAT_ID`, atomic-write (`os.replace`/`mkstemp`) blocks, `_load_queue()` copies.

### Reuse audit — grep by CORE PATTERN, not function name

Duplicates rename the wrapper but keep the guts, so grep the implementation signature across three tiers (in order), and name each hit with `file:line`:
1. Sibling scripts in the SAME dir (`profiles/*/scripts/`)
2. Vault scripts (`vault/**/scripts/`)
3. Skill-bundled scripts (`skills/*/scripts/`)

```bash
# credential / token readers
grep -rn "def get_token\|def _get_bot_token\|TELEGRAM_BOT_TOKEN=" scripts/
# HTTP / API senders
grep -rn "api.telegram.org\|def send_telegram\|urlopen\|parse_mode" scripts/
# queue / state IO + atomic write
grep -rn "def _load_queue\|os.replace\|mkstemp\|json.dump" scripts/
# scan-both-arrays iteration
grep -rn "pending.*history\|for arr in" scripts/
```
Hardcoded literals (chat IDs, base URLs, magic paths) repeated across files are the same finding class — flag the literal + every `file:line` it's copied to.

**Reuse smells specific to this profile's scripts:**
- Byte-identical helper bodies across N files (token parsers, plain-text senders) → extract ONE shared module, import from it.
- A **cron/entry-point script that became a de-facto import root** for siblings (e.g. `from review_telegram_sender import get_token` inside `fill_promo_tracking.py`) → one-directional, fragile coupling. Recommend promoting the shared helper to a neutral `*_common.py` (e.g. `tg_common.py`: token + send + `CHAT_ID`) that BOTH sides import — never leave a runnable cron script as the library root.
- Dead function parameter (e.g. `_patch_and_write(data, ...)` that ignores `data` and re-loads internally) → misleading signature, drop the param.
- Grouping/dedupe helper reused where its semantics are subtly wrong (group-by-text dedupe is correct for a broadcast/insight message sent once, but silently under-delivers in a per-item path where two distinct items can share identical text).

**Chesterton's Fence:** `git diff` / `git blame -L <lines>` the changed region first. The hardening/feature intent is usually legit — frame reuse findings as "collapse the duplication," never "revert the change."

### Finding report format (when user asks reuse + quality, skip nits)

Report each finding on one line, grouped into (A) Reuse and (B) Quality, lead with the highest-value consolidation, OMIT pure style nits:
```
file:line -> problem -> cost -> suggested fix | confidence: high/medium/low | risk: SAFE/CAREFUL/RISKY
```
- `confidence` = how sure the finding is real. `risk` = blast radius of applying the fix (SAFE = mechanical, CAREFUL = callers/schemas may differ, RISKY = behavioural).
- REVIEW-ONLY means no writes: report, do not patch.

4. Propose refactors by impact and risk
   - Low-risk/high-impact first: shared fetcher, shared week utils, shared store normalizer, deduplicated config imports.
   - Surface any hard-coded IDs/GIDs/sheet names as a migration risk.
   - Keep file-local behavior intact unless the user explicitly authorizes file edits.

5. Deliver findings
   - Classify issues into: duplication, inconsistency, hard-coded config, missing headless support, format drift.
   - Give actionable next steps in user's preferred plain style, with file paths and line ranges where useful.

## Applying safe refactors
If the user approves edits, prefer this sequence:
1. Edit shared code first: `_utils.py`, config files.
2. Update parser call sites to use shared helpers, removing local duplicates.
3. Read back modified files to confirm structure; do not run parsers.
4. Note migration risks: hard-coded sheet IDs/GIDs and prompt behavior (`input()` vs shared helper).

## Tooling quirk: path resolution for edits near this vault
Parser files under `C:\Users\khoans\Documents\Warren_OS_Local\.kilo\skills\` may fail with the direct file edit tool because of workspace path resolution. Workaround: use terminal with `cp` for backup + a small inline `python -` script to rewrite the file, then verify with `sed -n`. This keeps edits safe and reversible when direct patching is unavailable.

## Pitfalls

- **Verify dead-file claims on disk.** When a reviewer (or the user) flags a wiki/markdown file as decommissioned/deprecated/dead, read it and check the `status:` frontmatter plus body before trusting the claim. A review subagent once claimed `Labour_Cost_Hub.md` was decommissioned; it was actually `status: active` with live operating policies. Audits that act on unverified dead claims produce broken redirects and deleted links.
- **Reviewers reason from diffs, not repo truth.** Cross-check any reviewer assertion that a file or reference no longer exists or is broken against the actual file on disk before proposing a refactor that removes or rewrites it.

- **ripgrep / `search_files` KHÔNG traverse hidden `.scripts` / `.parsers` dirs (2026-07-28).** Khi audit `vault/.scripts/` (LEADING DOT), `search_files` + `find` qua ripgrep trả `0 matches` DÙ file tồn tại — subagent reviewers vấp phải, phải fallback `terminal grep` + `read_file` absolute path mới thấy. **Quy tắc audit vault này:** START bằng `terminal grep -rn "pattern" vault/.scripts/`; đừng tin `search_files` trả 0 cho hidden dir. Cross-check bằng `ls vault/.scripts/` nếu không chắc. (Không phải lỗi file — là blindspot của rg với dotfolder.)

## Commitments

- Treat parser files as read-only unless the user explicitly authorizes edits.
- Do not run parsers during an audit unless asked.
- Cite the inspected files; avoid guessing behavior.
- Prefer class-level helpers over per-file copy-paste fixes.
