# Git on Windows/MSYS — Quirks & Repro (stock-profile, 2026-07-09)

Hermes Desktop terminal runs git-bash/MSYS. `git` here has footguns that make a write look like it "didn't happen."

## Quirk 1 — MSYS path rejected ("not a git repository")

`git` rejects `/c/Users/...` MSYS paths in some subcommands with a misleading error:

```
$ git -C /c/Users/khoans/Documents/Personal_OS status --short
fatal: not a git repository (or any of the parent directories): .git
```

**Fix:** use Windows-style paths `C:/Users/...` (forward slashes OK):

```
$ git -C "C:/Users/khoans/Documents/Personal_OS" status --short   # works
```

Repro:
```bash
git -C /c/Users/khoans/Documents/Personal_OS rev-parse --is-inside-work-tree   # false / error
git -C "C:/Users/khoans/Documents/Personal_OS" rev-parse --is-inside-work-tree  # true
```

## Quirk 2 — .gitignore silently excludes a whole tree → "commit" does nothing

After editing `stock_vault/00_CORE_LOGIC/STOCK_MEMORY.md` and running `git add -A && git commit`:

```
On branch master
nothing to commit, working tree clean
```

But the file WAS changed on disk. Root cause: `.gitignore` line 15 ignores the entire `stock_vault/` tree:

```
$ git check-ignore -v stock_vault/00_CORE_LOGIC/STOCK_MEMORY.md
.gitignore:15:stock_vault/    stock_vault/00_CORE_LOGIC/STOCK_MEMORY.md

$ git ls-files --error-unmatch stock_vault/00_CORE_LOGIC/STOCK_MEMORY.md
error: pathspec '...' did not match any file(s) known to git
```

**Rule:** before reporting "committed", verify the file is actually tracked:
```bash
git ls-files --error-unmatch <path>   # exits 0 if tracked, error if ignored/untracked
git check-ignore -v <path>            # shows the .gitignore rule excluding it, if any
```
If ignored and Warren wants it tracked: `git add -f <path>` (force) or fix `.gitignore` — never assume.

## Quirk 3 — git rm vs rm (git restores deleted tracked files)

Tracked files removed with plain `rm -rf` get restored by git on next checkout/restore. Use:
```bash
git rm -r --cached <dir>   # unstage tracking
rm -rf <dir>               # delete on disk
git add -A && git commit   # commit the removal
```
Submodule-style refs (mode `160000`, shown by `git ls-files -s`) also need `git rm` — a plain `rm` leaves the gitlink. The tool's own `.git/<toolname>/` internals are NOT removed by `git rm -r <dir>`; sweep them separately with `rm -rf`.

## Pre-commit verification checklist
1. `git -C "C:/..."` (Windows path, not `/c/...`)
2. `git ls-files --error-unmatch <path>` → confirm tracked
3. `git check-ignore -v <path>` → confirm NOT ignored
4. `git status --short` → confirm the change shows
5. only then `git commit`
