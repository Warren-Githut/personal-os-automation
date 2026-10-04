# Candidate Grading — grading ONE candidate SKILL.md or prompt

Use when the user pastes a SKILL.md, a prompt, or asks "will this skill trigger",
"grade this skill", "weak description", "dead skill", "is this any good".

This grades ONE candidate artifact. It is not the installed-library audit — that is
steps 1-7 of the parent skill. Do not spawn a new domain skill from a grading result.

## Required input

If missing, ask ONE question, then stop:

1. Which file or paste? (path or full text)
2. What real job should it do? (one sentence)

Do not interview further when both are present.

## Layer A - Trigger

Pass only if the description includes all four:

- What the skill does
- Phrases the user would actually type, including the language the user speaks
- A negative boundary (when not to use it)
- No swallowing of sibling skills on the same machine

Fail if it is a catch-all, too narrow to ever match, has no "do not use" line, or its
trigger phrases collide with a sibling skill that already covers the same job.

To test the sibling claim, measure it: read the competing skills' `description` and
compare trigger phrases. Similar names are NOT overlap - shared trigger phrases,
shared outputs, or shared workflow steps are.

## Layer B - Procedure

Pass only if the body has:

- Imperative steps, one action per step
- A concrete stated output (name the shape: table, file, short verdict)
- Stops and bans
- None of: "handle appropriately", "as needed", "if necessary", "be careful"

Fail if it is philosophy with no steps and no output.

Then parse the file, do not eyeball it. A missing opening `---` fence makes every
field invisible to the loader while the file still looks correct in an editor.
Verify the frontmatter parses and the named `references/` and `scripts/` targets exist.

## Layer C - Three cases

Draft and mentally run three cases before reporting:

1. On-job - must load this skill and produce the stated output
2. Near-miss - must not steal a sibling skill; ask or refuse
3. Forbidden - must refuse or hand off

A near-miss that passes only because a sibling description happened to be longer is
NOT a pass - that is timing, not design, and it is the same defect Layer A names.

## Report shape

```
## Verdict
Pass | Fix description | Fix body | Merge/delete | Do not install

## Artifact
- name:
- job the user actually wants:

## Layer A Trigger
- Pass/Fail + one reason
- missing trigger phrases:
- missing boundary:

## Layer B Procedure
- Pass/Fail + one reason
- vague steps:
- unspecified output:

## Layer C Three cases
1. On-job - [user line] - Pass/Fail
2. Near-miss - [user line] - Pass/Fail
3. Forbidden - [user line] - Pass/Fail

## Minimum edit
- proposed description (one copy-paste block)
- 3-7 body lines to add or cut

## Will not do
- no git commit
- no new domain skill from this grading
```

## Minimum-edit discipline

Rewrite the whole file only when the user says so. Otherwise give the smallest diff:
one missing fence line, the two or three headers that lost their `##`, and the
boundary sentence that routes to siblings. Report the line count of the diff.

Before proposing any creation, run the pre-create overlap check. A candidate that
duplicates a skill already installed fails no matter how good its rubric reads.

## Agent bans

- Do not spawn a new domain skill "while we are here"
- Do not commit to GitHub or a vault
- Do not invent skill paths - discover the real skill root first
- Do not award A-F or 0-100 scores; use Pass / Fail plus a reason
- Do not execute scripts that belong to the artifact under audit
- Do not sign a third-party artifact with the user's name as author
