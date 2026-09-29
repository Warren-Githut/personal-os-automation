---
created: 2026-09-29
---
# Bulk Drift Reconciliation — SSOT ↔ mirror, many skills at once

> The multi-skill form of the Step 3 collision/direction problem. A guard reports
> "N drifted skills"; the job is to work out **which of the N are actually
> actionable**, sync only the machine-decidable ones, and hand the rest back.
> Never let a guard's raw count drive a bulk `cp`.

## The count is a bucket mix, not a defect list

A drift scan returns three statuses and they mean very different things:

| Status | What it usually means | Action |
|---|---|---|
| `MISSING` from mirror | **Often intentional** — the skill was archived or moved to a purge/quarantine dir on the mirror side | NO ACTION. Verify the archive location, then leave it |
| `DRIFT`, versions differ | Real, and the version field can usually decide direction | Sync, direction from the version comparison |
| `DRIFT`, versions equal | **Version is a label, not the truth** — content differs underneath | Must be classified further before touching |

A large `MISSING` count is the common trap. Check the mirror's archive and
quarantine directories before concluding those skills are missing: if the skill
resolves under a directory that is itself retired, the absence is the intended
state and "fixing" it resurrects retired content.

## Reuse the guard's own finder — do not reimplement it

Import the guard module and call its directory iterator, mirror lookup, and hash
function. A hand-rolled scan drifts from the tool that produced the report in
path handling (flat vs category-nested), normalisation (CRLF), and hash input, and
then your triage and the guard disagree about the same tree.

If the scan is a throwaway script, still make its summary go to **stderr** and
keep stdout as the data file. Redirecting both to one path silently overwrites
the dataset with the summary, and you then analyse stale data.

## Classify before you act

Group the actionable set by what mechanically decides the direction, and stop
there:

- **version fields compare** → they decide direction, sync it
- **one body is a strict subset of the other** → the superset side is newer, sync it
- **bodies differ in both directions** → a human merge; copying either way
  destroys the other side's work. These are the ones to hand back.

Any group whose direction you cannot justify from content is out of scope, no
matter how obviously stale it looks.

## Drop colliding entries, do not abort the batch

Re-run the collision check inside the apply step, not just when building the plan —
the working tree can change in between. When a small number of planned targets
are dirty, **remove them from the plan and continue** with the rest. Aborting the
whole batch over one dirty target wastes the work; the dropped entries simply go
back on the do-not-touch list, and the check has to be reported either way.

A dirty target is only disqualifying for the **files that are actually dirty**.
Confirm ownership per file (is the post-copy content identical to your source?)
rather than excluding the whole skill, or you will skip skills that were
untouched by the other session.

## Verify direction, not tree equality

The convergence predicate is: **every file in the source exists in the destination
with identical normalised content.** Comparing the two trees for equality in both
directions reports failure whenever the destination legitimately holds extra
local-only files.

Two related failure shapes to keep distinct, because they need different fixes:

- **destination path unknown** (`-`) — the mirror has no directory for this skill,
  usually because the whole category is absent. Derive the destination from the
  source's relative path, then create it. This is not a failed copy.
- **a verification report that contradicts itself** (an item flagged failed while
  its own "missing" and "differing" lists are both empty) — the verifier is wrong,
  not the data. A contradiction means the predicate is mis-specified; re-derive it
  before touching files.

Verify each copy by comparing normalised content, never by trusting the copy
command's success. Write a machine-readable receipt (applied / skipped / failed)
so the next step — commit scope — reads data instead of re-deriving it.

## Regenerate the scan after applying

Any dataset captured before the apply is stale. Re-run the scan and confirm the
delta equals the plan size. Two different failure modes share one signature here:
a skill already synced still appearing in the old dataset, and a stale dataset
hiding newly drifted skills. Both are fixed only by re-scanning, not by re-reading
the old file.

## Report the residual as a reasoned list

Close with a breakdown whose every bucket has a stated reason, so the leftover
work is self-explanatory: N resolved, N archived-by-design, N needing a human
merge, N deferred for collision. "There are still N drifted skills" is not a
handoff — it makes the next session redo the triage.
