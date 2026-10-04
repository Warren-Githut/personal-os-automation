# Consistency Scan Bloat Pattern — Option A (2026-07-24)

Condensed knowledge bank from the `CONSISTENCY_LOG.md` bloat-review session.
Umbrella: `vault-simplify-ssot` §8. Reusable when any vault scan/automation log
sits in a user-facing folder and accumulates noise.

## The decision frame
- Warren asked: "cái CONSISTENCY_LOG.md này quan trọng thật hay bloat?"
- Answer: **artifact = bloat, mechanism = valuable.**
  - Mechanism = `vault_consistency_nightly.py` (SSOT conflict / orphan / gap scanner, 0-token stdlib, runs 02:00 cron). It HAD caught a real SSOT conflict on 2026-07-20. Keep.
  - Artifact = `00_CORE_LOGIC/CONSISTENCY_LOG.md` — appended every scan even when "🔴0🟡0🟢0", and re-flagged intentional items (README.md ×7, 0-byte junk) because the script lacked a whitelist + auto-delete. Pure noise.
- Rule of thumb: separate *what the engine detects* from *how it logs*. Fix the
  logging scheme, never delete the detection engine.

## Option A design (deployed, commit 9dbbaf5 + 8efb586)
1. LOG_FILE → `vault/.consistency_log.md` (hidden dotfile, Obsidian hides dotfolders).
2. Rolling 7 days: `prune_log(7)` splits on `## 🔎 Consistency Scan — ` and drops
   blocks older than cutoff date.
3. Dedup + auto-resolve:
   - key = `f"{kind}|{msg}"` (stable).
   - new → log; re-opened (was resolved, now back) → log; known-still-open → skip;
     disappeared → `resolved=True` in state.
   - state persisted in `.consistency_state.json` (gitignored).
4. Whitelist `WHITELIST_NAMES = {README.md, google_review_weekly_sop.md, USER_GUIDE.md}`
   — excluded from BOTH orphan scan and 0-byte delete.
5. Auto-delete 0-byte: only `>24h` old, only in `SAFE_DELETE_DIRS`
   (`_inbox`, `30_KNOWLEDGE_BASE`, `00_CORE_LOGIC`, `10_OPERATION_DATA`),
   skipped on `--dry-run` / `--no-delete`.
6. Keep Telegram heartbeat (clean = green) — Warren rule "mọi cron tuyệt đối ko silent".

## Two real bugs caught (regex + guard)
- **Bug 1 — B2 orphan regex:** original `([\w]+\.md)` stopped at first `_`
  (captured "01" not "01_SSOT_01_Weekly_Revenue_Log.md"). Index uses markdown
  links `[name](path)` + backtick names. Fix:
  ```python
  for m in re.finditer(r"\[([^\]]+\.md)\]\(([^)]+\.md)\)", op_index):
      indexed_files.add(m.group(1)); indexed_files.add(m.group(2))
  for m in re.finditer(r"`([^`]+\.md)`", op_index):
      indexed_files.add(m.group(1))
  ```
  Verify: 15 operational logs resolve, 0 false-positive orphans.
- **Bug 2 — SAFE_DELETE_DIRS guard:** set had `"30_KNOWLEDGE_BASE/wiki"` but the
  guard compares `rel.parts[0]` (top-level = `"30_KNOWLEDGE_BASE"`) → wiki 0-byte
  cleanup never fired (dead code, fails safe). Fix: set contains top-level dirs.

## Reviewer-node gaps (forced critic — warren-profile rule)
1. `SAFE_DELETE_DIRS` wiki entry unreachable (Bug 2 above) — real, fixed.
2. Whitelist task spec said `USER_GUIDE.php`; code had `USER_GUIDE.md` (correct).
   Task description inaccuracy, code fine.
3. `entry_id` cosmetic non-uniqueness across runs — no functional impact, ignore.

## Test recipe (reproducible)
```bash
cd /c/Users/khoans/Documents/Warren_OS_Local/vault
# dry-run (no TG, no delete)
python3 .scripts/vault_consistency_nightly.py --dry-run
# live run writes hidden log + sends TG (dedup-safe)
python3 .scripts/vault_consistency_nightly.py
# simulate 0-byte wiki junk >24h and confirm auto-delete
JP="C:/Users/khoans/Documents/Warren_OS_Local/vault/30_KNOWLEDGE_BASE/wiki/_t/_j.md"
printf "" > "$JP"; touch -d "2026-07-20T10:00:00" "$JP"
python3 .scripts/vault_consistency_nightly.py
test -f "$JP" && echo STILL || echo REMOVED
```
Note: do NOT override VAULT_ROOT with `/c/...` MSYS path — Python Windows
mis-parses it as `\c\...` and `relative_to` crashes. Use the script default
Windows path or a Windows absolute path.
