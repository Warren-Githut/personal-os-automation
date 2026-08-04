# warren-profile Memory Layout (2026-07-15)

Exact on-disk tree for Warren's ops profile memory/context layers, plus the
git realities discovered while slimming SOUL.md + mirroring USER.md.

## File tree (relevant parts)

```
~/.hermes/profiles/warren-profile/
├── SOUL.md                          # agent identity — LOCAL, no git repo
├── .git/                            # CREATED 2026-07-15 via `git init`
├── .gitignore                       # excludes skills/ + caches
├── skills/                          # SEPARATE git repo (auto-backup cron)
│   ├── .git/                        #    NO remote → push impossible
│   ├── session-start/SKILL.md       # extracted from old SOUL §6
│   ├── compress-memory/SKILL.md     # extracted from old SOUL §2.2-2.5
│   └── ... (50+ other skills, many modified by curator)
└── memories/
    ├── MEMORY.md                    # built-in facts (§-delimited, injected each session)
    └── USER.md                      # MIRROR of vault 00_CORE_LOGIC/USER.md (created 2026-07-15)
                                     #   NOT in any git repo

Warren_OS_Local/                     # Hermes Desktop working dir (separate git repo)
├── AGENTS.md                        # canonical architecture pointer (REPO ROOT, not under vault/)
└── vault/
    ├── 00_CORE_LOGIC/
    │   ├── WARREN_MEMORY.md         # vault SSOT reference (dual-layer with built-in MEMORY.md)
    │   ├── USER.md                  # SSOT user profile (canonical for USER.md)
    │   ├── CONTEXT.md
    │   ├── TODAY.md
    │   └── pre_edit_checklist.md
    └── ...
```

## Key facts

1. **Dual memory layer is intentional** (Warren rejected collapsing it).
   - `memories/MEMORY.md` = built-in, auto-injected, gated by `memory.write_approval`.
   - `vault/00_CORE_LOGIC/WARREN_MEMORY.md` = vault SSOT reference, read at session start.
   - Override rule: vault WARREN_MEMORY.md wins on conflict.

2. **USER.md SSOT = vault file.** Mirror at `memories/USER.md` only stops the
   built-in layer from falling back to the stale generic `hermes/memories/USER.md`.
   Hand-sync mirror when vault changes. NOT auto.

3. **`hermes/memories/USER.md` (default profile root) is dormant** for named
   profiles — do not edit it expecting warren-profile to read it.

4. **Git reality:**
   - `warren-profile/` had NO `.git` before 2026-07-15 → `git init` + `.gitignore`.
   - `.gitignore` MUST exclude `skills/` (else nested-repo pollution) + `.usage.json`,
     `.bundled_manifest`, `.curator_*`, `.archive*`, `_archive_*`.
   - `skills/` repo: no remote → `git push` impossible there too.
   - `memories/` is in NO repo → USER.md mirror + SOUL.md (profile root) are the
     only version-controlled config files after `git init`.

5. **Dangling-ref traps caught while slimming SOUL.md:**
   - `vault/USER_GUIDE.md` does NOT exist → point to `Warren_OS_Local/AGENTS.md`.
   - `vault/AGENTS.md` is wrong path → actual is `Warren_OS_Local/AGENTS.md` (repo root).
   - Always `grep` the rewritten SOUL for every cited path + `§N` before declaring done.
