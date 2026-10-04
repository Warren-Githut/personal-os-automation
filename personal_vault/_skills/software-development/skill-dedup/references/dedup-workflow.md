# Dedup Workflow — exact commands + case studies

Profile skills root (Windows):
`C:/Users/khoans/AppData/Local/hermes/profiles/warren-profile/skills`

## Step 1 — find duplicate basenames
```bash
SK="C:/Users/khoans/AppData/Local/hermes/profiles/warren-profile/skills"
find "$SK" -name SKILL.md | sed "s#$SK/##; s#/SKILL.md##" \
  | awk -F/ '{print $NF}' | sort | uniq -d
```
→ Lists skill names appearing under 2+ paths.

## Step 2 — verify actual frontmatter `name:` (FALSE-POSITIVE TRAP)
Basename match is NOT proof of collision. Read the YAML `name:` of each hit.
```bash
for p in $(find "$SK" -name SKILL.md -path "*<name>*"); do
  echo "-> $p"; head -4 "$p"
done
```
Case: folder `agent-skills/` contained frontmatter `name: apply-agent-skills` — a DIFFERENT skill. Kept both. Not a dup.

## Step 3 — diff true duplicates (classify)
```bash
diff <(cat "$SK/<A>/SKILL.md") <(cat "$SK/<B>/SKILL.md") >/dev/null \
  && echo IDENTICAL || echo "DIFFERENT ($(diff "$SK/<A>/SKILL.md" "$SK/<B>/SKILL.md" | grep -c '^[<>]') changed lines)"
```
- stub-vs-full → merge stub's unique parts into full, delete stub.
- divergent fork (>~50 lines differ) → backup both, ASK user.

## Step 4 — backup before delete
```bash
BK="$SK/_archive_<name>_<YYYY-MM-DD>"
mkdir -p "$BK"; cp "$SK/<A>/SKILL.md" "$BK/A.SKILL.md"; cp "$SK/<B>/SKILL.md" "$BK/B.SKILL.md"
```

## Step 5 — delete (POSIX on Windows)
```bash
rm -rf "$SK/<folder-to-delete>"   # correct under bash
# rmdir //s //q ...  → FAILS (cmd syntax, not bash)
```

## Case study A — interview-me (stub-vs-full, SAFE)
- `skills/interview-me/SKILL.md` (319 lines, FULL — archetypes Warren + FBM refs)
- `skills/productivity/interview-me/SKILL.md` (34 lines, STUB — "extends skills/common/", broken base)
Action: merged stub's unique "grill-with-docs" (glossary + ADR) into top-level Step 4.5, updated frontmatter + Verification; `rm -rf` the stub. Result: 1 self-contained file.

## Case study B — 3 divergent forks (ASK, never auto-merge)
All 3 were full skills with different content; backed up, user chose:
- `stock-price-sync`: keep `stock/stock-price-sync/` (158 l), delete top-level (93 l)
- `test-driven-development`: keep `software-development/` v1.1.0 (393 l), delete top-level (383 l, 572 differing lines)
- `vault-restructure`: keep `note-taking/` v1.1 (291 l), delete `common/` v1.0 (249 l)

## Windows `patch` path quirk
`patch` with `/c/Users/...` is treated as RELATIVE → "outside the active workspace" error.
Fix: pass `C:\Users\khoans\...` (backslash, absolute). Same for `read_file`/`write_file` when target is outside the vault workspace.
