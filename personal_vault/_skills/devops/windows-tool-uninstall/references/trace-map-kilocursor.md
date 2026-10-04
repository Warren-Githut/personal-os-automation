# Trace map — 2026-07-09 Kilo Code / Cursor / VS Code purge

Generalize `<tool>` for any future uninstall. Starting checklist of where a Windows dev editor/AI tool hides.

## Survey (read-only first)
```
winget list | grep -iE 'cursor|kilocode|visualstudiocode'
ls -d /c/Users/<user>/AppData/Local/Programs/<tool>
ls -d /c/Users/<user>/AppData/Roaming/<Tool>
ls -d /c/Users/<user>/.<tool>            # e.g. ~/.cursor
ls -d /c/Users/<user>/.vscode            # VS Code home config (may hold kilo extension)
git -C "C:/vault" ls-files | grep -iE 'cursor|kilo|\.vscode'
git -C "C:/vault" ls-files -s tmp_agent_skills   # mode 160000 = gitlink
find /c/Users/<user> -maxdepth 4 -iname '*<tool>*'
```

## Actual traces found (Kilo/Cursor/VS Code)
- Vault git-tracked: `.kilo/` (4 files), `tmp_agent_skills/` (gitlink 160000)
- winget: `Anysphere.Cursor`, `Microsoft.VisualStudioCode` (EXE user) + `MSIX\Microsoft.VisualStudioCode_1.0.126.0_neutral__8wekyb3d8bbwe`
- AppData: `AppData/Local/Programs/cursor`, `AppData/Local/Programs/Microsoft VS Code`, `AppData/Roaming/Cursor`, `AppData/Roaming/Code/CachedExtensionVSIXs/kilocode.kilo-code-*`
- Home: `~/.cursor`, `~/.vscode` (holds `kilocode.kilo-code-7.3.54-win32-x64` extension), `personal_vault_kilo.archivelegacy_commands`
- Cache/config: `~/.cache/kilo`, `~/.config/kilo`, `~/.local/share/kilo` (.db), `~/.local/state/kilo`
- Temp: `AppData/Local/Temp/cursor-inno-updater-*.log`, `AppData/Local/Temp/kilo`, `Temp/case_battle_*/_kilo`
- Downloads: `CursorUserSetup-x64-3.0.13.exe`
- Other vaults: `Warren_OS_Local/.kilo`, `.kilocode`, `vault/.kilocode`
- Git internals left behind: `stock_vault/.git/cursor`, `stock_vault/.git/kilo`

## Verify clean
```
find /c/Users/<user> -maxdepth 5 \( -iname '*cursor*' -o -iname '*kilo*' \) | grep -viE 'node_modules|/lsp/'
winget list | grep -iE 'cursor|kilocode|visualstudiocode'
tasklist | grep -iE 'cursor|kilo|code'
git -C "C:/vault" status --short
```
