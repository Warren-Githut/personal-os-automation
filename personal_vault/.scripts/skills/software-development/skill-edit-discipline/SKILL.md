---
name: skill-edit-discipline
description: Safe discipline for reading, patching, and creating Hermes agent skills — and verifying external system state before acting on it. Use before any skill_view→patch, skill_manage write, or push to an external system (mem0, cron, API, Telegram, Calendar).
version: 1.0.0
author: Hermes
trigger: "Before patching/creating any skill, or before pushing/asking about an external system (mem0/cron/API/Telegram/Calendar)."
category: software-development
---

# skill-edit-discipline — Safe Skill Edit + Verify-Before-Act

> **Purpose:** Two hard-won lessons from 2026-07-19 (stock-profile session). Both are forms of "don't trust stale state — verify the real thing on disk before you act."

---

## Pitfall 1 — skill_view returns STALE / TRUNCATED content 🚨

`skill_view(name)` can return OLD or CUT-OFF content for a skill that was already edited on disk. If you use that returned content as your mental base and then `patch`, you get **duplicate sections** or wrong overwrites.

**RULE — before any skill patch:**
1. `skill_view` for structure (fast) — but do NOT trust it as complete.
2. **MANDATORY `read_file` the full SKILL.md path** (and `references/` if needed) to see the true on-disk content.
3. Compare: if skill_view is missing a section that disk has → use read_file as your patch base.
4. After patch → `read_file` again to confirm no duplicate / no wrong overwrite.

**Real incident:** stock-deploy-capital got a duplicate 5A-5E block because patch used stale skill_view output. Fixed by merge + dedup.

---

## Pitfall 2 — VERIFY external system state BEFORE acting (don't trust memory text) 🚨

Memory files (STOCK_MEMORY.md, MEMORY.md, USER.md) may contain OLD references to external systems that were later disabled/deleted by the user. If you act on those stale references, you look stupid and annoy the user.

**RULE — before asking / pushing / touching ANY external system (mem0, cron, API, Telegram, Calendar, external DB):**
1. **VERIFY on disk first:** does the config file exist? does the data dir exist? is the provider enabled in config.yaml / mem0.json?
2. If the system **does NOT exist / was disabled / was deleted** → **SKIP that step**, remove the stale reference from the memory file, and **DO NOT ask the user about it**.
3. If unsure → `terminal` check (`ls` / `find` / `grep config`). Do not trust memory text.
4. This is a direct consequence of NEVER TRUST LLM / verify everything — applied to tool/infra STATE, not just parsed data.

**Real incident:** Hermes asked "push mem0?" even though Warren had told it to delete mem0. Root cause: trusted STOCK_MEMORY.md line "8. Push mem0" + "scripts/mem0-status.sh" (script didn't exist either). Disk reality: no mem0.json, no FAISS dir, no `memory: provider=mem0` in config.yaml. Fix: removed all mem0 references, recorded this lesson.

---

## Pitfall 3 — Script cited in SKILL.md: verify it lives in THAT skill's folder (orphan-duplicate trap) 🚨

When a SKILL.md cites `scripts/<name>.py`, the path is RELATIVE to that skill's own folder. If you "fix" the cite based on a different listing, you can pick the WRONG filename — because the SAME skill basename may exist in TWO places (e.g. canonical `mkt/combo-calculation-gp/` + orphan `combo-calculation-gp/` at skills root), each with a DIFFERENT script name.

**RULE — before patching any script citation in a SKILL.md:**
1. Note which folder the SKILL.md you are editing actually lives in (the `skill_dir` from `skill_view`).
2. `find <skills_root> -name "<cited_script>.py"` → see EVERY copy on disk, with full paths. Do NOT trust a prior `ls -R` from a different cwd — `ls -R` and `find` disagree when duplicates exist.
3. Confirm the script exists in the SAME skill folder as the SKILL.md. If yes → the cite is already correct, do NOT change it.
4. If the cited name is missing from that folder but present in a DIFFERENT folder with the same skill basename → you've found an **ORPHAN DUPLICATE skill folder**. DO NOT guess which name is "right" — flag it (zone 🟡) for Warren to decide cleanup. The canonical one is usually the category-nested path (`mkt/`, `ops/`, etc.); the root-level one is usually the stale orphan (often no SKILL.md of its own).
5. Never patch a cite to match an `ls -R` snapshot taken from another working directory.

**Real incident (2026-07-19, warren-profile):** Editing `mkt/combo-calculation-gp/SKILL.md` §7 which cited `evening_combo_roi.py`. Bootstrap `ls -R` showed `combo_gp_calc.py` in that folder → patched cite to `combo_gp_calc.py`. Then `grep -rn evening_combo_roi` surfaced `./combo-calculation-gp/scripts/evening_combo_roi.py` (orphan folder at skills root, no SKILL.md). Panicked, reverted cite to `evening_combo_roi.py`. Final `find` revealed: canonical `mkt/combo-calculation-gp/scripts/combo_gp_calc.py` EXISTS (correct), orphan `combo-calculation-gp/scripts/evening_combo_roi.py` is stale. Reverted cite back to `combo_gp_calc.py` (matches its own folder). Two wrong turns from not running `find` first.

---

## Pitfall 4 — GIT COMMIT/PUSH after skill edits: verify tracked status FIRST (skills/ may be gitignored) 🚨

When Warren says "git commit push" after you edited skills, do NOT assume the skill changes are committable. In `warren-profile`, the `skills/` folder is listed in `.gitignore` (line `skills/`) → **all skill edits are LOCAL-ONLY by design and are NOT tracked by that repo's git**.

**RULE — before any git commit/push triggered by skill work:**
1. `git status --short` to see what is actually staged/modified.
2. `git check-ignore skills/` (or `git ls-files skills/`) → confirm whether skill changes are tracked.
3. **If `skills/` is ignored:** report "skill changes saved local, not in repo" and STOP. Do NOT `git add -f skills/` unless Warren explicitly overrides. Do NOT blindly commit the unrelated files `git status` happens to show (e.g. `config.yaml`, `cron/jobs.json`, `scripts/*.py`) — those are OUT OF SCOPE of the skill task and committing them violates SSOT (commit rác / unrelated changes).
4. Always run the **Commit-Push Self-Gate (SOUL §5.3)** regardless — print Q1 (SSOT simplify) + Q2 (automate readiness), wait for Warren's explicit "push"/"ok".

**Real incident (2026-07-19, warren-profile):** After a 5-slice skill refactor (extract `marketing-council`, patch `ops-mkt-manager-os`/`promo-eval`/`combo-calculation-gp`), Warren said "OK GIT COMMIT PUSH ĐI CON". `git status` showed `config.yaml`, `cron/jobs.json`, `vault_consistency_nightly.py` (unrelated to the task). `git check-ignore skills/` → `skills/` ignored. Correct action: did NOT commit; asked Warren which scope (A: nothing / B: force-add skills / C: commit unrelated). Warren's intent was the skill work, which is already saved locally.

## Post-edit QA bundle (warren-profile convention)

When Warren directs a skill edit/refactor and then says to QA it (or "chạy code-review + simplification + battle-test + ab-test + debugging"):
- **code-review-and-quality** → 5-axis adapted for prompt/markdown (Correctness/Readability/Architecture/Security/Performance); for pure markdown edits, verify YAML frontmatter parses + no dead `references/` links + cross-skill links resolve.
- **code-simplification** → mark SKIPPED if zero code was written/modified (markdown-only). Don't simplify for its own sake.
- **battle-test --scope skills** → YAML valid %, link integrity %, script compile %. No live vault mutation.
- **ab-test** → compare BEFORE (duplicate logic) vs AFTER (SSOT extracted) variant; recommend winner on maintainability/drift-risk/token-cost.
- **debugging-and-error-recovery** → reproduce → root cause → fix → guard. Verify deletions with `ls`/`test -d`, NOT `find` alone (find may show stale entries after `rm -rf` due to cache/race — seen 2026-07-19: orphan `combo-calculation-gp/` deletion reported "STILL THERE" by `find` but `ls` confirmed GONE).

## Pitfall 5 — Partial table-row match in `patch` truncates content 🚨

When patching a markdown **TABLE ROW**, matching only the beginning portion (e.g., `| **Rule Name** 🚨 |`) WITHOUT including the rest of the row content causes the patch tool to replace the matched fragment — effectively **DELETING everything after the `|` on that line**. The row ends up truncated: `| **Rule Name** 🚨 |` with no content.

**RULE — before patching any table row:**
1. `read_file` the FULL row content — from first `|` to last `|` on that line. Do NOT assume the row is short.
2. Include the **ENTIRE row** in both `old_string` and `new_string` of the patch call.
3. If inserting a new row BETWEEN two existing rows, use the COMPLETE row above or below as the anchor, not a partial match.
4. After patch → `read_file` the patched area to confirm no truncated rows.

**Detection after patch:** `grep` for rows that end abruptly with `|` and no content after:
```bash
grep -n '^|.*|$' file.md
```
If a row has a second `|` with nothing after it, it's truncated.

**Real incident (2026-07-21, warren-profile SOUL.md):** Patching to insert `Line-by-Line Compute` between `Freeze Gate` and `Step & Cross-Verify discipline`. Old string only matched `| **Step & Cross-Verify discipline** 🚨 |` (beginning of row). Patch replaced just that fragment → full content of Step & Cross-Verify row got wiped. Fixed by restoring the full row content in a follow-up patch.

## Pitfall 6 — Gate/rule added to one profile SOUL.md but NOT synced to others 🚨

When you add a new gate/rule/token to ONE profile's SOUL.md (§5 Core Rules), the other profiles operating under the same agent need the same gate. Otherwise the agent behaves inconsistently across profiles — obeying the gate in `warren-profile` but ignoring it in `stock-profile` or `personal_profile`.

**RULE — after adding any gate/rule to one SOUL.md:**
1. Identify ALL active profiles: `ls "$LOCALAPPDATA/Hermes/profiles/"` (warren-profile, stock-profile, personal_profile, etc.)
2. `read_file` the §5 Core Rules table in each profile's SOUL.md
3. If the new gate is **absent** from another profile → patch it in with profile-appropriate examples (stock: P/E, valuation; personal: chi tiêu, health)
4. After all patches → `read_file` each to confirm no truncation (see Pitfall 5)
5. If a profile lacks a SOUL.md entirely → create one with the gate included

**Real incident (2026-07-21):** `🧊 FREEZE:` token added to `warren-profile/SOUL.md`. Warren said "cross profile, làm cho stock-profile và personal-profile luôn." Stock-profile and personal_profile SOUL.md both lacked the Freeze Gate. Patched both in one batch.

## Pitfall 7 — Quên backup skill lên vault sau khi tạo/sửa 🚨

AppData `skills/` nằm ngoài vault git repo (đã gitignored). Nếu tạo/sửa skill xong mà KHÔNG copy backup vào `vault/_archives/skills/` → khi mất máy / đổi laptop / profile reset → **mất toàn bộ skill**. Warren dùng laptop công ty — rủi ro thực tế.

**RULE — SAU MỖI LẦN tạo/sửa skill/parser/script (SOUL §5 Skill Archive Gate 📦):**
1. Copy SKILL.md → `vault/_archives/skills/<name>_SKILL_backup_YYYY-MM-DD.md`
2. Nếu skill có `scripts/` hoặc `references/` → copy cả thư mục
3. `git add vault/_archives/skills/` + `git commit -m "backup: <name>"` + `git push`
4. In token `📦 ARCHIVE: ✅ <name>` ra chat — thiếu token = vi phạm

**Real incident (2026-07-21):** 19 skills sửa trong ngày nhưng chưa có backup nào trong vault. Nếu Warren mất máy ngày mai → mất hết 19 skill. Backup batch + tạo gate này.

## Pitfall 8 — `patch` on YAML frontmatter: matching VALUE without KEY strips the key 🚨

When patching YAML frontmatter (the `---` block at the top of SKILL.md), fuzzy matching can match a **VALUE fragment** (e.g., the description text) WITHOUT its KEY prefix (`description:`). The patch tool replaces the matched text → the key is stripped, corrupting the frontmatter.

This is the YAML equivalent of Pitfall 5 (table-row truncation): in structured text, never match only the value — always include the key/delimiter.

**RULE — before patching any YAML frontmatter line:**
1. **Always include the full YAML key** in `old_string` (e.g., `description: Refines raw ideas...`, NOT just `Refines raw ideas...`).
2. **For adding a NEW field to frontmatter** (e.g., `related_skills` where none exists): match the line IMMEDIATELY BEFORE the closing `---` delimiter, and include the delimiter in `old_string` as context anchor. Example:
   ```
   # old_string (includes key + next line delimiter):
   trigger: Warren says "check"...
   ---
   # new_string:
   trigger: Warren says "check"...
   related_skills: [idea-refine]
   ---
   ```
3. **For modifying an EXISTING field** (e.g., adding to `related_skills`): match the ENTIRE existing line including the key and all values, then replace with the full new line.
4. After patch → verify with `grep`:
   ```bash
   grep "related_skills\|^[a-z]" file.md | head -20
   ```
   If you see a bare text line without a key prefix (e.g., `Use when an idea is still vague...` instead of `description: Use when...`), you've stripped a key.

**Real incident (2026-07-22, warren-profile skill-bundle-audit session):** Patching `idea-refine/SKILL.md` to add `related_skills: [explore]`. `old_string` matched just the description VALUE text (`Use when an idea is still vague, when you need to stress-test...` → `---`) WITHOUT the `description:` key prefix. Patch tool replaced this fragment → description text became a bare line, YAML key `description:` was lost. Fixed by re-adding `description:` prefix in follow-up patch. Lesson: always include the YAML key in old_string.

**Batch verify after bulk frontmatter patches:**
```bash
for f in skill1 skill2 ...; do
  echo "--- $f ---";
  grep "related_skills" "skills/$f/SKILL.md";
done
```
This catches missing/malformed `related_skills` lines across all patched files instantly.

## Pitfall 9 — `patch` with `replace_all=True` on a NON-UNIQUE anchor DESTROYS the file 🚨

When `old_string` matches the anchor in MANY places (e.g. a short string like `SHEET_NAME = "..."` that appears 38× as a substring inside longer lines), `replace_all=True` does NOT replace just that anchor — it **replicates the entire new_string block at every match location**, splicing duplicates into the middle of unrelated lines. Result: file balloons to hundreds of garbage lines, syntax error, unrecoverable by another patch.

**Real incident (2026-07-23, warren-profile ops-review session):** Task = insert a `STORE_DISPLAY_NAME` dict + `format_store_name()` helper into `review_response_handler.py` after the `SHEET_NAME = "05_Google_Review_Weekly_Log"` line. Con used `patch` with `old_string="SHEET_NAME = \"05_Google_Review_Weekly_Log\"\n\n"` + `replace_all=True`. The string appeared as a substring in ~38 lines → `replace_all` injected the full block (dict + function + 2 blank lines) at ALL 38 spots, including mid-line inside other functions. File went from 395 → 1200+ lines of duplicated garbage, `SyntaxError: invalid character '─'`. Con had to `git checkout -- <file>` to restore, then insert with a SAFE method (below).

**RULE — inserting a block next to a line that may appear multiple times:**
1. **NEVER use `replace_all=True` with a short/substring anchor.** `replace_all` is only safe when the anchor is a COMPLETE unique line/block you intend to replace EVERYWHERE.
2. **For a ONE-TIME insert:** read the file (`read_file` full, or `terminal cat`), then use `terminal` python with an **assert on exact count**:
   ```python
   s = open(path, encoding='utf-8').read()
   anchor = 'UNIQUE_ANCHOR_STRING\n'   # must be a full unique line/block
   assert s.count(anchor) == 1, f'anchor not unique: {s.count(anchor)}'
   s = s.replace(anchor, anchor + NEW_BLOCK, 1)
   open(path, 'w', encoding='utf-8').write(s)
   ```
   The `assert s.count(anchor)==1` FAILS FAST if the anchor is ambiguous — before any damage. This is the safe pattern; `patch replace_all` is the dangerous one.
3. **If `patch` reports "Found N matches"** for an insert anchor → STOP. Do NOT add `replace_all=True`. Switch to the terminal-python-assert method above (or `write_file` the merged full content after a full read).
4. **After ANY bulk edit to a `.py`/`.json`:** run a syntax/parse check IMMEDIATELY before declaring done:
   ```bash
   python3 -c "import ast; ast.parse(open('path/to/file.py',encoding='utf-8').read()); print('SYNTAX_OK')"
   ```
   If the file was corrupted → `git checkout -- <file>` (if tracked) or restore from the last known-good backup, then re-insert safely.
5. **Then verify the inserted symbol actually works** (e.g. `from review_response_handler import format_store_name; assert format_store_name('LU3')=="L'Usine Le Thanh Ton"`), not just that it parses.

**Detection:** after a `replace_all` patch, if `git diff --stat` shows the file grew by 2×+ unexpectedly, or a `SyntaxError`/`invalid character` appears → you hit this. Restore and re-insert via terminal-python.

## When this skill applies

- You loaded a skill via `skill_view` and are about to `patch` it.
- You are about to `skill_manage(action='write_file' | 'edit' | 'create')`.
- You added a new gate/rule to one profile's SOUL.md → sync to all other profiles before considering the task done.
- A memory file mentions an external system and you're about to invoke / push / ask about it.
- You catch yourself about to repeat a step from a template (e.g. compress-memory step "Push mem0") without checking if that system is still alive.
- **You just created or edited a skill/parser/script → MUST run Skill Archive Gate 📦 (see Pitfall 7)**

## Boundaries

| Always | Never |
|--------|-------|
| read_file full skill before patch | patch from stale skill_view output |
| terminal-verify external system exists before push/ask | ask user about / push to a deleted/disabled system |
| remove stale references after discovering they're dead | trust memory text over disk state |
| `find <skills_root> -name "<script>.py"` before patching a script cite | patch a script cite to match an `ls -R` from a different cwd |
| confirm cited script lives in the SAME skill folder as the SKILL.md | guess the "right" script name when a duplicate/orphan folder exists |
- **backup skill to vault/_archives/ + commit push after every create/edit** | **skip archive gate — mất skill khi đổi máy** |
| **insert code block into a file where the anchor may repeat → use terminal-python with `assert s.count(anchor)==1`, NEVER `patch replace_all=True`** | **`replace_all=True` on a non-unique anchor — corrupts the file (Pitfall 9)** |

## Pitfall 10 — Đừng vội "merge 2 skill" — scope blast-radius + phân biệt mode trước 🚨

Khi thấy 2 skill cùng keyword, đừng đề xuất "merge / dedup over add" ngay. Session 2026-07-25: con đọc 2 file gốc, kết luận `code-simplification` trùng với `simplify-code` → đề xuất merge. Sai: (1) grep FULL tree mới ra `code-simplification` dính ~25 files (skills + reference docs + 1 memory), merge = 25-file churn; (2) 2 skill này KHÔNG trùng — khác cost/intent tier (`code-simplification` = inline cheap + L'Usine pitfalls; `simplify-code` = 4-agent parallel, 4 altitudes). Đúng là mode-differentiated → KEEP BOTH, cross-link + router route (Option 1 light-converge).

**RULE — trước mọi đề xuất merge/converge 2 skill:**
1. **Grep FULL tree cho CẢ HAI tên:** `skills cron memories pending` + vault `00_CORE_LOGIC`. Đếm hit per-file. Naive read 2 file gốc bỏ sót cross-references (vd thật: 25 files, không phải 2).
2. **Phân biệt TRUE DUPLICATE (cùng job/cost → merge) vs MODE-DIFFERENTIATED (khác cost/intent → KEEP BOTH, cross-link + router route).** Warren "merge over keep" chỉ áp dụng cho true duplicate — mode-differentiated thì YIELD.
3. **Check bundled shadow:** xóa profile override có thể resurrect bản bundled thiếu custom content (L'Usine pitfalls). Survivor = profile override.
4. **Edit-guard:** `using-agent-skills` manually-authored → runtime có thể từ chối tự patch (memory f02db674) → prep diff thủ công cho Bố.
5. **Decision:** hit >5 files → light-converge (cross-link), KHÔNG destructive merge. Quy trình + decision table đầy đủ → `references/skill-merge-scoping.md`.
