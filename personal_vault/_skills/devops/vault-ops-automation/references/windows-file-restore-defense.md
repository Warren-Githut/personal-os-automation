# Windows File Restoration Defense

Discovered in session 2026-06-26 when deleted files (_kilo/, _hermes_vault_index.md,
README.md, USER_GUIDE.md, tests/, Clippings/, _drafts/) kept reappearing.

## Root Cause

The `remotely-save` Obsidian plugin (enabled in `community-plugins.json`) syncs vault
to a remote (S3/WebDAV/OneDrive). When files are deleted locally, the plugin pulls
them back from the remote — effectively undoing the deletion.

## Detection

```bash
cat vault/.obsidian/community-plugins.json | grep remotely-save
```

## Fix

1. Temporarily disable remotely-save (remove from `community-plugins.json`)
2. Delete the files with PowerShell
3. Add file patterns to `.gitignore`
4. Re-enable remotely-save after sync

## Reliable Deletion on Windows

```powershell
# Preferred — native Windows, handles all cases
powershell.exe -Command "Remove-Item -Path '<path>' -Recurse -Force -ErrorAction Stop"

# Avoid — may fail silently due to MSYS filesystem caching
rm -rf <path>
```

## `.gitignore` Defense

After deletion, add patterns to prevent re-tracking:
```
# Windows auto-restore protection
stale-folder/
stale-file.md
```

Make sure to use `git add <specific-file>` not `git add -A` after deletion,
otherwise restored files get re-added to the index.

## Obsidian Folder Hiding (when folder must stay but stay hidden from file explorer)

| Method | Scope | User Action Needed |
|--------|-------|--------------------|
| `attrib +h <folder>` (Windows) | File Explorer + Obsidian (if setting OFF) | Tắt "Show hidden files" in Settings → Files & Links |
| `userIgnoreFilters` in `.obsidian/app.json` | Search + Quick Switcher + Graph | None |
| CSS snippet `display: none !important` | File Explorer | Enable snippet in Settings → Appearance → CSS snippets |
| Rename to `.folder-name` | Completely hidden by Obsidian | Update all code paths referencing old name |

**CSS snippet pattern:**
```css
.nav-folder[data-path="folder-name"],
div[data-path="folder-name"] {
  display: none !important;
}
```
Place at `.obsidian/snippets/hide-folder.css`.
