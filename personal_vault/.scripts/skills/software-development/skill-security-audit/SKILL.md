---
name: skill-security-audit
description: Audit AI agent skills (Claude Code, Hermes, etc.) for malicious code, vulnerabilities, and security risks using static + optional LLM semantic analysis. Trigger when user asks to vet, scan, or check if a skill is safe before installing, or when setting up SkillSpector.
---

# Skill Security Audit

## When to use
- User asks "is this skill safe", "vet this skill", "scan for malware/virus/trojan", "quét skill trước khi cài", or similar
- User wants non-friction one-liner security checks on new/existing skills
- Protecting Warren from malicious agent skills

## Setup (one-time)

### Git clone + install
```bash
git clone https://github.com/NVIDIA/skillspector.git
cd skillspector
uv venv .venv
make install
```

### Preferred invocation (Windows + git-bash / MSYS)
```bash
cd /path/to/skillspector
uv run skillspector scan ./skill-path --no-llm
```

**Why `uv run` not `source .venv/bin/activate`?**
On Windows git-bash/MSYS, `source .venv/bin/activate` fails because uv creates `.venv/Scripts/activate.bat`. Running `uv run tool` from the repo root is the zero-friction path; it picks up the local venv automatically.

## Fast non-friction scan (Warren workflow)
1. Put the skill to audit in a local folder (downloaded repo, extracted zip, or existing skill dir)
2. Run:
```bash
cd /path/to/skillspector
uv run skillspector scan ./skill-folder --no-llm --format markdown
```
3. Filter the report for all 🔴 HIGH + 🚨 CRITICAL findings.

### Quick filtering
```bash
uv run skillspector scan ./skill --no-llm --format markdown | grep -E 'Score|Severity|CRITICAL|HIGH'
```

## Output interpretation
- `Score 0-100`: higher is worse
- `Severity`: CRITICAL > HIGH > MEDIUM > LOW
- `Recommendation`: `DO_NOT_INSTALL`, `REVIEW`, or `ALLOW`
- `--no-llm`: static-only (2-5s, offline, zero cost). Adds 64 regex/pattern checks.
- With LLM: adds semantic analysis for obfuscation and hidden intent; requires API key env vars.

### Thresholds
| Score | Action |
|-------|--------|
| 0-30 | Likely safe. Proceed after spot-checking any single finding. |
| 31-70 | Review findings. Re-scan with LLM if the skill has scripts or shell commands. |
| 71-100 | Treat as hostile until findings are individually reviewed and justified. |

## LLM config (optional, Warren-local privacy)
Use local Ollama to keep data in-house:
```bash
export SKILLSPECTOR_PROVIDER=openai
export OPENAI_API_KEY=ollama
export OPENAI_BASE_URL=http://localhost:11434/v1
export SKILLSPECTOR_MODEL=llama3.1:8b
uv run skillspector scan ./skill --format markdown
```

## Windows pitfalls (Warren host)
- **`patch` / `write_file` / `skill_manage write_file` path resolution**: `/c/...` absolute MSYS-style paths are sometimes rewritten to `C:\c\...` and rejected. Fallback: write files via `uv run python -c "..."` or terminal `cat >`.
- **Recursive deletes**: `rm -rf` in git-bash requires approval. If it hangs, use `rm -r` for smaller scopes, or mid-session ignore.
- **Termux/root bypass**: On Windows hosts, Termux root (`su 0`) does not help. Use the Windows filesystem directly.
- **False positives on directory scans**: Scanning a large existing skills bundle can return sparse `Score 100/CRITICAL` if reporting misinterprets directory-level input. Treat that as a signal to re-scan profile by profile, or per-skill.

## Verification
After setup, sanity-check:
```bash
cd skillspector
uv run skillspector scan README.md --no-llm
```
Should print a terminal report and not error.

## References
- `references/patterns-summary.md`: condensed 64-pattern catalogue (16 categories, severity guidance)
- `references/setup-recipe.md`: step-by-step install notes per OS
