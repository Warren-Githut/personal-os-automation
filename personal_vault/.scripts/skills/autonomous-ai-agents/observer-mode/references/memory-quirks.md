# Memory Tool Quirks & Workarounds

## `memory replace` fuzzy matching is unreliable
The `replace` action uses a 9-strategy fuzzy matcher but fails on entries that look identical. Common failure modes:
- Whitespace differences (trailing spaces, `\n` vs `\r\n`)
- Unicode characters that appear identical but aren't
- Multi-line entries where line breaks shift

**Workaround:** When `replace` fails, use the three-step flow:
1. `memory remove` with the unique `old_text` substring
2. `memory add` with the fully consolidated replacement text
3. If the entry is large, trim it BEFORE adding (check char count first)

## Memory budget management
- Single consolidated entry beats multiple fragmented entries
- When at >90% and adding new content: remove old entry first, then add consolidated version
- Aim for 1,900–2,000 chars on a 2,200 limit — leave room for incremental updates
- Pruning priority: live decisions > structural facts > preferences

## Trainings with large payloads
When user delivers a block of training text that would exceed the limit:
1. Read carefully for genuinely new facts vs. restated existing facts
2. Remove the existing entry first
3. Write one tight consolidated entry
4. Drop the least time-sensitive items first (status snapshots > structural rules > active cases > communication protocol)

## Vault data freshness rule
Status snapshots (W23 revenue, weekly COL) age in ~1 week. When memory is near-limit, drop stale snapshots first — active cases are most time-sensitive.
