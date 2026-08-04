# Markdown SSOT Section Splice — Reusable Recipe

For generator scripts that rewrite a named `## ` section inside a human-readable
SSOT markdown (P&L breakdown, wiki pages, dashboards with inline data). Copy-paste
and adapt. Captured 2026-07-10 after a session lost TARGET/COST-STRUCTURE sections
and duplicated FULL-LINE-ITEM via bad splices.

## Correct idempotent splice (Python)

```python
def splice_section(main_path, new_section, target_header):
    lines = open(main_path, encoding="utf-8").read().split("\n")
    ti = [i for i, l in enumerate(lines) if l.startswith(target_header)]
    assert len(ti) == 1, f"{target_header} count={len(ti)} (expect 1)"
    ti = ti[0]
    # next ## section STRICTLY after the target
    ni = [i for i, l in enumerate(lines) if l.startswith("## ") and i > ti][0]
    head = lines[:ti]
    tail = lines[ni:]          # starts at section AFTER target — never re-includes target
    out = "\n".join(head) + "\n" + new_section + "\n\n" + "\n".join(tail)
    open(main_path, "w", encoding="utf-8").write(out)
    # POST-WRITE ASSERT: every unique ## header still appears exactly once
    chk = open(main_path, encoding="utf-8").read().split("\n")
    for h in (target_header, "## 🧮 COST STRUCTURE", "## 🎯 TARGET vs ACTUAL",
              "## 📋 FULL LINE-ITEM"):
        c = sum(1 for l in chk if l.startswith(h))
        assert c <= 1, f"{h} count={c} after splice (duplicate!)"
```

## When the file is already corrupted (duplicate/lost sections)

1. `cp` the broken file to `_broken_backup.md` (recovery safety).
2. `git checkout -- <file>` to reset to last committed clean state.
3. Re-run ALL generators in dependency order (FULL LINE-ITEM -> COST STRUCTURE store
   -> TARGET), splicing each exactly once with the recipe above.
4. Delete `_broken_backup.md` only after verifying the rebuilt file is correct.

## JS verification for inline HTML dashboards (Chart.js etc.)

`python` lint won't catch JS syntax errors. Extract the script block and run the real parser:

```python
import subprocess
html = open(dash_path, encoding="utf-8").read()
js = html.split('<script>')[1].split('</script>')[0]
r = subprocess.run(["node", "--check", "-"], input=js, capture_output=True, text=True)
assert r.returncode == 0, r.stderr[:200]
```

If `node` is absent, flag it — don't claim JS-valid. This caught real bugs (unclosed
f-strings, bad regex) that markdown-structure checks missed.

## Known traps (this session)

- `ni` computed as "next ## " WITHOUT `i > ti` -> can select an EARLIER section ->
  `tail` re-includes the target -> duplicate after `head + new + tail`.
- Splicing `head[:ti] + new + tail[anchor:]` where anchor is a DIFFERENT section than
  the one after the target -> drops intervening sections.
- Subagent review false-positive: keyword "typo" that matches the SOURCE DATA spelling
  (e.g. CSV has "Unemployeement insurance") is NOT a bug — grep the real source before
  "fixing".
- Heredoc `python3 - <<'PY'` blocks: remember to `import subprocess` / `import tempfile`
  INSIDE the heredoc (module-level imports in the outer script are NOT in scope).
- The verify-gate may re-fire on every edit of an HTML file. Running `node --check`
  (real parser) + structural assertion is sufficient fresh evidence; stop looping after
  ~3 consistent passing checks.
