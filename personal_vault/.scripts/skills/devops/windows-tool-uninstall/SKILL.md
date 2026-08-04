---
name: windows-tool-uninstall
description: Thoroughly remove a Windows dev tool or AI coding editor (Kilo Code, Cursor, VS Code, or any) so nothing remains and git does not restore it. Use when Warren says delete/uninstall/remove an editor, "chỉ dùng Hermes", or wants a tool purged. Covers git gitlinks (mode 160000), winget dual entries (EXE + MSIX), AppData, home dotfiles, and leftover .git internals.
---

# Windows Tool / Editor Uninstall (thorough)

When Warren says "xóa [tool]", "uninstall [tool]", "chỉ còn xài Hermes", or otherwise wants a dev editor / AI tool gone — remove it COMPLETELY. Half-removal lets git restore tracked files or leaves the app launchable. This is the deterministic path.

## When to use
- "Xóa hết Kilo Code / Cursor", "chỉ dùng Hermes Desktop"
- "Uninstall VS Code", "remove [any editor]"
- Any request to purge a Windows dev tool and guarantee it stays gone (including from git)

## Survey first (read-only — never delete yet)
Build the blast-radius map BEFORE touching anything:
1. `winget list` — find installer id(s). One app may have MULTIPLE entries (EXE user + MSIX store).
2. AppData: `ls -d /c/Users/<user>/AppData/Local/Programs/<tool>` , `AppData/Roaming/<Tool>`
3. Home dotfiles: `ls -d /c/Users/<user>/.<tool>` , `/c/Users/<user>/.vscode` , `/c/Users/<user>/.cursor`
4. Vault git-tracked: `git -C "C:/path/to/vault" ls-files | grep -iE 'cursor|kilo|\.vscode'`
5. Nested git repos / gitlinks: `git -C <vault> ls-files -s <folder>` — mode `160000` = gitlink (submodule-style reference).
6. Other vaults (Warren_OS_Local etc.) for `.kilo` / `.kilocode` / `.cursor`.

If ambiguous (e.g. `.vscode` could be VS Code vs a Cursor extension, or a nested repo isn't obviously junk), ASK via clarify before deleting. Confirm scope when VS Code app is involved.

## Execution order
1. **Git-tracked first** (safe + prevents restore):
   - `git -C "C:/vault" rm -r --cached --quiet .kilo tmp_agent_skills` then `rm -rf` the folders, then `git add -A` + `git commit -m "remove <tool>"`.
   - Gitlinks (mode 160000): `git rm -r --cached` removes the index reference; then `rm -rf` the working dir. Commit. Git will NOT restore.
2. **winget uninstall** (background, slow): `winget uninstall --silent --accept-source-agreements <id>` for EACH entry. Uninstall ALL entries for one app.
3. **Physical remnants**: `rm -rf` AppData/Local/Programs/<tool>, AppData/Roaming/<Tool>, ~/.cursor, ~/.vscode, Downloads installer .exe, AppData/Local/Temp/<tool>* logs, /c/Users/<user>/<tool> dotfiles, /c/Users/<user>/.cache/<tool>, .config/<tool>, .local/share/<tool>, .local/state/<tool>.
4. **CRITICAL — leftover .git internals**: after `git rm -r`, git leaves `.<vault>/.git/<tool>` (e.g. `.git/kilo`, `.git/cursor`). These are git's own bookkeeping, NOT removed by `git rm`. `rm -rf` them manually.
5. Other vaults: `rm -rf` their `.kilo` / `.kilocode` / `.cursor` (tool config, not personal data).

## Verify (must pass before reporting done)
- `find /c/Users/<user> -maxdepth 5 \( -iname '*cursor*' -o -iname '*kilo*' \) | grep -viE 'node_modules|/lsp/'` → blank
- `winget list | grep -iE 'cursor|kilocode|visualstudiocode'` → NONE
- `tasklist | grep -iE 'cursor|kilo|code'` → no running
- `git -C "C:/vault" status --short` → clean

## Pitfalls
- **Git MSYS path**: `git -C /c/Users/...` (MSYS path) FAILS with "fatal: not a git repository". Use Windows-style absolute path: `git -C "C:/Users/khoans/..."`. Same for `cd`.
- **winget via bash background swallows output** ("stdin is not a tty"); you won't see success/failure. Always re-verify with `winget list` separately — don't trust the background job's exit code.
- **VS Code home config is `.vscode`** and may contain a Kilo/Cursor extension (`kilocode.kilo-code-*`). Deleting `~/.vscode` removes VS Code config too — confirm Warren wants VS Code gone before `rm -rf ~/.vscode`.
- **Gitlink gotcha**: a folder tracked as mode `160000` is a nested git repo reference. `git rm` it, then `rm -rf` the folder (plain `rm` leaves the index entry; git restores on checkout).
- **Never `rm` a git-tracked file without `git rm`** — plain `rm` leaves it in the index; git restores it later. Always `git rm` + commit.
- **Temp/cache dotfiles**: `~/.cache/<tool>`, `~/.config/<tool>`, `~/.local/share/<tool>`, `~/.local/state/<tool>` are easy to miss.

## Support files
- `references/trace-map-kilocursor.md` — condensed trace map from the 2026-07-09 Kilo/Cursor/VS Code purge (starting checklist, generalize the tool name).
- `scripts/sweep_traces.sh` — deterministic probe: finds cursor/kilo/vscode/code traces + winget + processes. Run to verify clean.

## Notes
- This is OS/environment cleanup, distinct from vault tidy (`tidy` skill) though it overlaps on `.kilo` vault files. Use this skill for editor/tool removal; use `tidy` for vault content org.
- Durable state: since 2026-07-09 Warren uses ONLY Hermes Desktop. Kilo/Cursor/VS Code are gone.
