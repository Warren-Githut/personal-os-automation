---
name: warren-vault-discovery
description: >-
  Fan out across Warren's vaults before claiming it is absent.
trigger:
  - Warren names a system/file/GSheet/pipeline you can't find on first search
  - about to say "no system exists" / "can't write, no permission"
  - cross-vault or cross-profile lookup needed
---

# Warren Vault Discovery Discipline

## When to use
Warren operates across several vaults and Hermes profiles. A system he references
may live in a different vault than the one your session is rooted in. Before
declaring absence or impossibility, run the discovery protocol below.

## Warren's vault/profile map (as of 2026-08)
| Vault / Profile | Root | Domain |
|---|---|---|
| Personal_OS (personal_profile) | `C:/Users/khoans/Documents/Personal_OS/personal_vault` | health, family, finance, personal |
| Warren_OS_Local (warren-profile) | `C:/Users/khoans/Documents/Warren_OS_Local/vault` | L'Usine F&B ops — reviews, COL, PL, wastage, item sales |
| Stock_OS (stock-profile) | separate vault | VN equities (purged from Personal_OS 2026-07) |
| Skills (warren-profile) | `C:/Users/khoans/AppData/Local/hermes/profiles/warren-profile/skills/ops/ops-review` | ops-review pipeline |

## Discovery protocol (run BEFORE any "not found" claim)
1. Identify which domain Warren's reference belongs to (F&B ops → Warren_OS_Local;
   health/family → Personal_OS; equities → Stock_OS).
2. Search that vault's `vault/` tree with `search_files` (file_glob + content).
3. If not found, search the OTHER vaults too — do NOT stop at the session's home vault.
4. Also search `AppData/Local/hermes/profiles/*/skills/` for the governing skill
   (skills often hold the canonical write/read logic, not just the vault md files).
5. Only after ALL of the above come up empty may you tell Warren "no system found"
   — and even then, ask him to confirm the intended destination.

## 🚨 Pitfalls (from real sessions)
### P1 — Single-vault search → false "no system exists"
Searching only Personal_OS and concluding Warren's F&B review system doesn't exist
is WRONG. The `ops-review` system lives in Warren_OS_Local. Always fan out across
vaults before declaring absence. [Warren correction 2026-08-23: "sao con ko biết vậy"]

### P2 — Conflating a readonly parser's OAuth scope with the write handler's scope
A GSheet pipeline may have BOTH a readonly parser (for weekly reporting) AND a
write handler (for appending new rows). Reading only the parser and seeing
`spreadsheets.readonly` does NOT mean the pipeline can't write. Find the actual
write function (e.g. `_append_to_gsheet` in `vault/.scripts/review_response_handler.py`)
and check ITS scope. Declaring "can't write, SA is readonly" from the parser alone
is a false conclusion. [Warren correction 2026-08-23: "CHECK KỸ ĐI, SAO KHI GỬI QUA
TELEGRAM THÌ CON GHI ĐƯỢC, GIỜ BỐ GỬI TRỰC TIẾP THÌ CON KO LÀM ĐƯỢC"]

### P3 — Chat-paste ≠ "no pipeline"
When Warren pastes a review/entry directly into the Hermes chat (no `[ops-review]`
Telegram tag), it is the **Manual Chat Intake** flow, NOT an absence of system.
The same write path (`_append_to_gsheet`) applies. Treat chat-paste as a valid
intake channel, not a gap.

### P4 — Path/rglob does NOT follow symlinked directories
Skill collections are often assembled with symlinks (a shared command library
linked into several profiles). `Path.rglob()` / `glob.glob()` will not descend
into a symlinked directory, so every skill behind that link reports as missing
while it is right there. The failure is silent — you get a clean, confident,
wrong "not found" list.

Symptom: a skill you loaded earlier in the same session, or know exists, is
absent from a programmatic inventory. That contradiction is the tell — the
search is broken, not the artifact.

Fix: build the index with `os.walk(root, followlinks=True)`, and index by
`<skill_dir_name> -> .../SKILL.md` (a skill's name is its **directory**, not a
`.md` filename). Guard against the second trap: `rglob(name)` may return the
directory, so check `.is_file()` before reading, or you will report a directory
as a missing file.

Corollary for scripts: the same applies to any user content dir reachable only
through a link. Verify with a direct-path existence check before concluding
absence.

## References
- `references/ops-review-write-path.md` — concrete ops-review GSheet write path,
  schema, and the readonly-vs-write scope split, so future sessions don't repeat P2.
