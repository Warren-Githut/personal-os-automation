# Obsidian Table Breakers — condensed reference

Obsidian renders a markdown table only while consecutive lines all start with `|`.
Any interruption closes the table and the remainder prints as raw `| |`.

## Breaker 1 — blank / blockquote inside a table
- Blank line between two `|` rows → table splits. Delete the blank.
- `>` blockquote immediately after a `|` row (no blank between) → Obsidian
  treats it as table continuation → breaks. Fix: separate with a blank line,
  or put the note AFTER a `---` separator. Safe shape:
  ```
  | last row | ... |
  > note about the table
  <blank>
  next section
  ```

## Breaker 2 — emoji inside a cell
Only these break render (strip to text per WARREN_MEMORY d413):
- 🔴 → `R`, 🟡 → `Y`, ✅ → `G`, ⏳ → (drop / "Pending")
- Keep emoji in bullets, headers, HTML comments.
- NOT breaking (leave alone): `→ ← ↑ ↓`, `─ │ ┌`, `★ ☆`, `≥ ≤ ≈ × −`, `*`.

Pitfall: a linter that flags any codepoint ≥ U+2190 as "emoji" will falsely
flag every `→` mapping cell. Use a whitelist + `>= 0x1F300` only.

## Breaker 3 — column drift
Header `| a | b | c |` has 4 pipes (3 cols). A data row must match. Fix the
offending row (missing/extra `|`, or an unescaped `|` inside a cell value).

## Quick diagnosis
```
python vault/.scripts/vault_table_render_lint.py <file-or-folder>
# exit 1 = issues listed as  ## path (N)  /  Lnn: message
```
Lint does NOT detect mojibake — check encoding separately (see mojibake-reverse.md).
