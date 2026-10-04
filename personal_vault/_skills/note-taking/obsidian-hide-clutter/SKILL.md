---
name: obsidian-hide-clutter
description: "DEPRECATED — use obsidian-vault-hygiene instead. userIgnoreFilters does NOT hide from the file explorer tree; only .dotfolder rename does. Trigger: 'Obsidian rối', 'vault lộn xộn', 'ẩn file rác'."
version: 0.2.0
author: Hermes Agent + Warren
license: MIT
platforms: [windows, linux, macos]
---

> ## ⚠️ DEPRECATED — READ THIS
> **This skill's original core claim is WRONG and will waste your turns.** `userIgnoreFilters` (Settings → Excluded files) does **NOT** hide folders from the Obsidian **file explorer tree** — it only hides from Search / Graph View / Unlinked Mentions / Quick Switcher. If Warren says "vault rối, ẩn folder", leading with `userIgnoreFilters` will fail; Warren will report "vẫn hiện".
> **The correct, proven method is the `.dotfolder` rename** (rename `scripts` → `.scripts`, etc.) — Obsidian auto-hides any dot-prefixed folder from the tree. Full workflow + verification + `__pycache__` prevention: **see skill `obsidian-vault-hygiene`** (canonical). Use that skill, not this one.
> This stub is kept only so the curator can consolidate it into `obsidian-vault-hygiene`. Do not follow the steps below as primary method.

# Obsidian — Hide Clutter (DEPRECATED — see obsidian-vault-hygiene)

**DO NOT USE userIgnoreFilters as the primary hide method.** See top warning. Kept for historical reference only.

## Why this stub is wrong
The original Core rule claimed `userIgnoreFilters` "hides matches from the file explorer, graph view, AND in-vault search." Session 2026-07-15 proved this false via liteparse-OCR of the actual Obsidian Excluded-files UI text: it only affects Search/Graph/Unlinked Mentions. Folder containers in the file tree remain visible. Warren confirmed "vẫn hiện" repeatedly.

## Correct approach (summary — full detail in obsidian-vault-hygiene)
1. Rename junk folders to `.dotfolder` (e.g. `parsers` → `.parsers`, `_accumulation` → `._accumulation`).
2. Bulk-update hardcoded path refs in `.py`/`.md`/`.json` (Python `.replace`, not sed).
3. Prevent `__pycache__` regen: `sys.dont_write_bytecode = True` in run scripts + `.gitignore` with `__pycache__/`.
4. Reload Obsidian → dotfolders vanish from tree.
5. Optional: keep `userIgnoreFilters` too (redundant Search/Graph hiding).

## Step 1 — Inspect (read-only, still valid)
List the vault root and busiest data folder:
```bash
ls -la "/c/Users/khoans/Documents/Warren_OS_Local/vault"
ls -la "/c/Users/khoans/Documents/Warren_OS_Local/vault/10_OPERATION_DATA"
```

## Step 2 — Rescue real content (still valid)
Before deleting stray folders (e.g. `~`), find real files inside:
```bash
find "/c/Users/khoans/Documents/Warren_OS_Local/~" -type f
```
Session 2026-07-15 found `lusine-ops/SKILL.md` inside `~` → rescued to `_TRASH_RESCUE/` before `rm -rf`.

## Step 5 — Verify (ad-hoc, still valid pattern)
Write `hermes-verify-*.py` to `C:/Users/khoans/AppData/Local/Temp/`. Classify HIDDEN/VISIBLE via Obsidian's regex logic; assert critical `.md` VISIBLE. Run + cleanup.

**Pitfall:** don't verify Windows reserved-name deletion (`nul`, `con`) with `os.path.exists` — always True. Use `os.listdir`.
