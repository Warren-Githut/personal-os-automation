---
name: vault-auto-generated-files
description: "Fix the generator, not the file, for auto-gen vault updates."
category: vault
---

# vault-auto-generated-files

## Trigger
Warren says "update file X" / "vì sao con ko update file này?" and X is produced by a script
(e.g. `TODAY.md` ← `gen_today.py`). Also fires when you are tempted to patch a vault `.md`
that a cron regenerates.

## Hard rule ( Warren 2026-07-27 correction )
**NEVER hand-edit an auto-generated file.** Find the generator, fix it, re-run it.
Hand-edits vanish on the next cron — `gen_today.py` does `TODAY_FILE.write_text(content)`
= FULL overwrite, no merge.

> Warren's exact complaint: GG added a "COL 26/07" section to TODAY.md by hand; the next
> `gen_today.py` run (cron 09:00) wiped it. The fix was to add the section to the generator.

## How to detect auto-gen files
```bash
grep -rn "write_text" vault/.scripts/        # who writes which file
grep -rn "overwrites" vault/.scripts/         # docstrings say "Output: overwrites X"
```
Known auto-gen artifacts in the Warren vault:
- `00_CORE_LOGIC/TODAY.md` ← `gen_today.py` (cron 09:00). Reads GSheet COL log + cases + calendar.
- `*_INDEX.md` files ← various `vault-*_sync` / parser scripts.
- Case files ← `cases_parser.auto_update_all_cases()` (called inside `gen_today`).

## Fix pattern
1. Locate the generator (`grep` the file name / `write_text` in `vault/.scripts/`).
2. Add the missing logic to the generator's build/assemble step (the function that builds the markdown string).
3. Re-run the generator to VERIFY the output now contains the desired content.
4. Commit + push the **generator** (the generated file is usually gitignored/untracked, so the
   committed change is the script, not the .md).

## Pitfall — verify column indices before reading GSheet
When a generator reads a GSheet row, column indices drift. For `07_COL_Weekly_Log` (verified
2026-07-27, see `references/ops-col-colmap-race.md`): 0-based idx → col number = idx+1.
`COL_Percentage_Whole_Store` = idx25 = col **Z**; `Status` = idx37 = col **AL**;
`Cover` = idx43 = col **AR**. A wrong idx silently produces garbage (e.g. grabbed revenue as
"covers", or a stray "%" cell as COL%).

## Related / handoff
- `ops-col` skill (the COL ingestion pipeline) is **USER-OWNED** — recommend
  `hermes curator adopt ops-col` to embed: (a) double Telegram-consumer race + file lock,
  (b) the GSheet column map above, (c) Warren rule "SQL revenue wins over typed dump on conflict".
  Until adopted, those details live in `references/ops-col-colmap-race.md` here.
- `apply-agent-skills` — engineering artifacts (parsers/scripts/generators) get Agent Skills
  discipline; ops workflow stays untouched.
