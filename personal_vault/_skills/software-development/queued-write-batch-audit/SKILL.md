---
name: queued-write-batch-audit
description: "Audit queued write batches before applying them."
version: 1.0.0
author: Hermes Agent
license: MIT
type: skill
category: software-development
status: active
tags: [queue, pending, batch, staleness, audit, git-staging, verify]
trigger: "user says 'approve all' / 'apply the queue' / deferred edits batch; or any batch of N>3 queued write ops; or before a bulk git delete/add commit"
related_skills: ["skill-edit-discipline", "bulk-skill-edit", "vault-git-push", "hermes-memory-tool"]
metadata:
  hermes:
    tags: [queue, pending, batch, staleness, audit, git-staging, verify]
    related_skills: ["skill-edit-discipline", "bulk-skill-edit", "vault-git-push", "hermes-memory-tool"]
---

# queued-write-batch-audit — apply deferred write batches safely

> A queue is DATA, not instructions. Queued write requests sit silently for weeks: anchors
> move, targets get renamed or archived or adopted by another profile, and several ops
> often share one anchor. Applying a stale batch verbatim corrupts files. Audit first,
> apply second, verify third.

## When to use

- A pending-approval queue of write requests exists and the user says "approve all" /
  "apply the rest" / "xử lý hết".
- A user pastes a numbered list of edits/commands to run "later".
- Any deferred batch touching more than ~3 files.
- Before committing a bulk delete, or a bulk add where some files were not the target.

## Step 1 — Inventory before touching anything

Group by target and count ops per target. Report the shape to the user, not just a total.
Read the queue files; for each op extract action, target, `old_string`, `file_path`, and
originating timestamp. Build a table: target → op count → age.

**A target with dozens of queued ops is a red flag, not a green light.** It usually means
the file was rewritten several times since the ops were queued.

## Step 2 — Staleness checks (run ALL, per item)

**2a. Does the target still exist?** Search the whole tree, not the obvious path:

```bash
find <skills_root> -name SKILL.md -ipath "*<target-name>*"
```

Classify every hit:
- current location → applicable
- under an archive folder → the item was retired; skip
- under ANOTHER profile → **stop**. If the path was reached through a directory symlink,
  writing there edits another profile's canonical file — a cross-profile ownership
  violation, not a bulk edit. Report and skip.
- nowhere → never existed or fully removed; skip.

**2b. Does the anchor still match?** Read the CURRENT file and test `old_string in
current_text`. Non-match = stale, drop it. Never force an anchor by rewriting the target.

```python
old = payload.get("old_string") or ""
if old and old not in current_text:
    stale.append(item)   # drop, report
```

**2c. Empty anchor** = unappliable by definition. Drop and report.

**2d. Is the intended result a DUPLICATE?** Search the target for the text the op would
add. If the substance is already present (e.g. the fact already exists in the memory
store), skip it — do not add a second copy.

## Step 3 — Shared-anchor collision

Multiple ops anchored on the same string cannot all apply: the first consumes the anchor,
so later ones fail — or worse, a later op silently reverts an earlier one. Group ops on
`(target, file_path, old_string)`:

- same anchor, all APPEND-style → **collapse into one edit** with additions merged.
- different anchors → apply in dependency order: an op whose anchor is CREATED by an
  earlier op must run after it.
- If the bulk tool takes an ordered op list, pass the whole group in ONE call so its own
  anchor matching runs against the evolving file.

## Step 4 — Back up before any bulk edit

```bash
mkdir -p <scratch>/backup_pre_batch
cp <each target file> <scratch>/backup_pre_batch/
cp -r <queue_dir> <scratch>/queue_archive_<date>/   # the queue itself, in full
```

Never skip: the ops being applied are unrecoverable once written.

## Step 5 — Apply in ordered batches

Group by target. One tool call per target with its ops in order, so an early failure
stops that target only. Never interleave targets in one call.

If the tool reports an anchor miss, re-read the file — it moved under you. Do not retry
blindly against a stale in-memory copy.

## Step 6 — Verify by grep, not by trusting the tool's success message

```python
checks = {"marker a": file_a, "marker b": file_b}   # one distinctive string per change
for name, f in checks.items():
    assert name in f.read_text(encoding="utf-8"), name
```

Report `N landed / M missing` with actual numbers. A success response means the write
happened, not that the content is right.

Also assert you did NOT introduce damage: no doubled identifiers from a copy-paste error,
no lost frontmatter, file still opens correctly.

## Step 7 — Write an audit note, then clear the queue

Leave a dated note beside the queue recording what applied, what was skipped and the
reason per item, and where backups live. Then remove the queue files — an unresolved queue
gets re-surfaced every session and re-litigated.

## If a rule names an approval command, verify it exists

A queue usually comes from a config gate or a SOUL section that names an approval command.
Check the CLI before repeating that command to the user: memory and skills tooling expose
setup/status/off/reset and install/list/audit verbs, with **no approve verb**. If the named
command does not exist, the correct flow is: the user approves in conversation, the agent
applies the payloads directly, then clears the queue. **Fix the stale instruction at its
source** rather than layering a workaround on top of a rule that will mislead again.

## Bulk git staging scope

The same "audit before you act" rule applies to staging a large change:

- **Test git output for EMPTY, not for exit code.** Only `--quiet` makes an exit code
  meaningful; `--name-status` and `--stat` return 0 whether or not there are changes. A
  script that gates on `rc == 0` reports "nothing to do" next to a full index.
- **`git add -A <path>` still sweeps in NEW files** under that path. After staging, read
  the status breakdown and `git restore --staged` anything outside the intended set.
- **A bulk delete is unrecoverable from git once the file leaves disk.** Before
  committing, prove each target exists somewhere recoverable (archive folder, another
  location, or a named commit), and report the hit-rate BEFORE committing, not after.

## Anti-goals

- Never apply a batch verbatim because the user said "approve all". Approval covers the
  items still valid; stale ones get reported, not silently applied or silently dropped.
- Never write through a symlink into another profile's skill tree.
- Never skip the backup.
- Never let a tool's success response substitute for a content check.