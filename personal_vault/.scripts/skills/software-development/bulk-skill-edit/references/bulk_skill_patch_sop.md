# bulk_skill_patch_sop.md — reusable snippet + git recipe

## Reusable Python (run via terminal, not execute_code)

```python
from pathlib import Path
import re

ROOT = Path(r"C:\Users\khoans\AppData\Local\hermes\profiles\warren-profile\skills")

# target subdir -> domain string for the block
mapping = {
    "personal-commands/stock-capture": "broker report, price sheet, BCTC",
    # ... add all targets
}

HEADING = "## MANDATORY VERIFY GATE"
def make_block(domain, nl):
    lines = [
        HEADING + " (rule: never trust LLM, verify everything)", "",
        "After EVERY parser run that reads Excel/CSV/PDF ([DOMAIN: " + domain + "]), "
        "MUST run verify-parser-output gate BEFORE reporting numbers or committing.", "",
        "1. Independent recompute (fresh script, different method).",
        "2. Cross-assert EVERY number vs LLM output.",
        "3. Category-drop scan: count raw rows vs filtered; flag dropped.",
        "4. Emit VERIFY_RESULT: PASS|FAIL + dropped count. Temp hermes-verify-*.py, clean after.",
        "5. FAIL -> LLM wrong until proven. Fix logic, re-run, re-verify.", "",
    ]
    return nl.join(lines)

report = []
for rel, domain in mapping.items():
    p = ROOT / rel / "SKILL.md"
    if not p.exists():
        report.append("MISSING: " + rel); continue
    raw = p.read_bytes()
    nl = b"\r\n" if b"\r\n" in raw else b"\n"
    text = raw.decode("utf-8")
    if HEADING in text:
        report.append("SKIP (present): " + rel); continue   # idempotent: no dup
    block = make_block(domain, nl.decode())
    m = re.search(r"^## Reference", text, re.MULTILINE)      # prefix: Reference(s)
    if m:
        pos = m.start()
        prefix = text[:pos]; suffix = text[pos:]
        if not prefix.endswith(nl.decode() * 2):
            prefix += nl.decode() * (1 if prefix.endswith(nl.decode()) else 2)
        new_text = prefix + block + suffix
    else:
        new_text = (text if text.endswith(nl.decode()) else text + nl.decode()) + nl.decode() + block
    p.write_bytes(new_text.encode("utf-8"))
    report.append("PATCHED: " + rel)
print("\n".join(report))
```

Run: `python3 "C:/Users/khoans/.../patch.py"` then `rm` the script.

## Verify
```
cd "C:/Users/khoans/AppData/Local/hermes/profiles/warren-profile/skills"
grep -rl "MANDATORY VERIFY GATE" .
# expect = N targets + 1 (the defining skill self-mentions it)
```

## Git staging (skills/ is its OWN repo — do NOT git add -A)
```
cd "C:/Users/khoans/AppData/Local/hermes/profiles/warren-profile/skills"
git add path/to/file1.md path/to/file2.md ...   # explicit only
git diff --cached --name-only                    # confirm == targeted count
git commit -m "feat(...): add standardized block to N skills"
# leave 80+ unrelated dirty files alone; no remote by default
```
