# Skill Doc/Code Drift Detection

Reusable recipe for reviewing a Hermes skill that ships a Python runner. Catches documented commands the runner rejects, dead `references/*.md` links, and stale tool/cron names. Used 2026-07-13 to find 3 real bugs across `code-review-and-quality`, `battle-test`, `ab-test`.

## Steps (run from skill dir)

```bash
SK=<skill_dir>   # e.g. $LOCALAPPDATA/hermes/profiles/warren-profile/skills/ab-test

# 1. Every flag/choice in SKILL.md Commands block must exist in runner
grep -nE "add_argument" "$SK/scripts/"*.py
#    -> read each parser.add_argument("--x", choices=[...]); compare against SKILL.md

# 2. Every references/*.md cited in SKILL.md must exist on disk
grep -noE "references/[A-Za-z0-9_-]+\.md" "$SK/SKILL.md" | sort -u | while read -r f; do
  p="$SK/${f##*: }"; [ -f "$p" ] || echo "DEAD REF: $f"
done

# 3. Stale tool/cron names the user later deprecated
grep -niE "ops-lint" "$SK/SKILL.md" || echo "no stale ops-lint ref"

# 4. Compile all scripts (catches broken runners)
python3 -m py_compile "$SK/scripts/"*.py && echo "COMPILE OK"
```

## Failure classes
- **Documented flag not in runner `choices`** -> `argparse` error at runtime. e.g. `ab-test --type memory` when runner only accepts `parser/prompt/vault`. Fix: drop from Commands, keep methodology in `references/`, add note "runner supports X only".
- **Dead `references/*.md`** -> broken link; especially embarrassing if the skill itself warns "stale refs are bugs". Fix: create the file or remove the cite.
- **Stale tool/cron name** -> references a retired component. Fix: rename to current (e.g. `ops-lint` -> `ops-index-sync --check-only`).

## Rule of thumb
After editing ANY skill's docs, re-run steps 1-2 before declaring done. Documented-but-unsupported commands are Critical doc bugs, not cosmetic.
