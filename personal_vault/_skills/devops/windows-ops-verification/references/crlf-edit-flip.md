# CRLF Edit-Flip — Repro + Byte-Precise Edit (2026-07-13)

Obsidian vaults on Windows are CRLF. With no `.gitattributes`, the committed blob can be
MIXED (e.g. 229 CRLF + 1 bare LF on line 1). Editing via `patch`/`write_file`
rewrites the file uniformly → git shows a WHOLE-FILE flip that is NOT your edit.

## Repro (what happened)
```
$ git diff --stat vault/00_CORE_LOGIC/CONTEXT.md
 vault/00_CORE_LOGIC/CONTEXT.md | 458 ++++++++++++++++++++---------------------
 1 file changed, 229 insertions(+), 229 deletions(-)
```
Reality: only 2 table rows changed. The flip = eol normalization noise.

## Byte probe that proved it
```python
import subprocess
head = subprocess.run(["git","show","HEAD:vault/00_CORE_LOGIC/CONTEXT.md"],
                       capture_output=True).stdout
work = open("vault/00_CORE_LOGIC/CONTEXT.md","rb").read()
def eol(b):
    c={"CRLF":0,"LF":0}
    for ln in b.split(b"\n")[:-1]:
        c["CRLF" if ln.endswith(b"\r") else "LF"] += 1
    return c
print("HEAD", eol(head))   # {'CRLF':229,'LF':1}  <- the 1 bare LF = line 1
print("WORK", eol(work))   # {'CRLF':229,'LF':0}  <- uniform
```
The single bare-LF line in HEAD is the entire "flip".

## CORRECT edit technique (byte-precise, no re-encode)
```python
path = "vault/00_CORE_LOGIC/CONTEXT.md"
data = bytearray(open(path,"rb").read())

old = (b"| Context Weekly Update | Mon (auto) | `/ops-weekly-report` Phase 7 | Auto-updates CONTEXT.md \xc2\xa75 |\r\n"
       b"| Weekly Connections | Sun | Hermes LLM | Cross-domain synthesis t\xe1\xbb\xab logs |\r\n"
       b"| Deep Research | On-demand | `/ops-deep-research [topic]` | Reads entire vault \xe2\x86\x92 belief, contradiction, gap, question |\r\n")
new = (b"| Context Weekly Update | Mon (auto) | `/ops-weekly-report` Phase 7 | Auto-updates CONTEXT.md \xc2\xa75. *(Weekly Connections c\xe5\xa9 \xc4\x91\xe3\xa3 merge v\xe3\xa0o \xc4\x91\xe3\xa2y t\xe1\xbb\xab W26 \xe2\x80\x94 cross-domain synthesis n\xe1\xba\xb1m trong `weekly_ops_synthesis.md` \xc2\xa7Cross-Domain Connections)* |\r\n"
       b"| Deep Research | On-demand | `/ops-deep-research [topic]` | Reads entire vault \xe2\x86\x92 belief, contradiction, gap, question |\r\n")

assert data.count(old) == 1, "old segment not found exactly"
open(path,"wb").write(data.replace(old, new))
```
Note: copy the EXACT bytes (including `\r\n` and UTF-8 multibyte) from the file —
don't hand-type. Use `repr()` of the segment you read.

## VERIFY (semantic, not stat)
```python
import difflib, subprocess
head = subprocess.run(["git","show","HEAD:<path>"],capture_output=True).stdout.decode("latin-1")
work = open("<path>",encoding="utf-8").read()
d = [l for l in difflib.unified_diff(head.splitlines(True), work.splitlines(True), n=2)
     if l[:1] in "+-"]
print("".join(d) if d else "NO DIFF")   # only your real edit lines
```

## `.gitattributes` nuance
```
*.md text eol=crlf
*.py  text eol=lf
*.json text eol=lf
*.csv  text eol=lf
```
- `git check-attr eol -- <file>` → `eol: crlf` = attribute recognized. GOOD.
- BUT it does NOT retro-heal a mixed HEAD blob. Test-edit simulation STILL showed
  a 228-line diff after adding the rule. `git add --renormalize <file>` also failed
  to rewrite the index blob in-session.
- To actually fix existing blobs: a ONE-TIME repo renormalize —
  `git add --renormalize . && git commit -m "chore: normalize eol via .gitattributes"`.
  This is a separate, larger commit (touches every tracked text blob). Out of scope
  for a single edit — propose separately, never bundle with the content edit.

## Rule of thumb
On a CRLF/Obsidian vault with no `.gitattributes`, a `git diff --stat` whole-file
flip = eol noise, NOT your edit. Verify by byte blob comparison, not by stat.
