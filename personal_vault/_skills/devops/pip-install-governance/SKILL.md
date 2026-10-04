---
name: pip-install-governance
description: Governs Python package installation on Windows in this environment. Prefer user-local installs, verify readiness before rerun, never rerun a failed build loop.
---

# pip install governance

## When to use
- Installing a dependency for the active Hermes profile or Python user environment.
- Retrying after a failed `pip install` that involved native/Rust/MSVC builds.

## Rules
1. Always resolve this Python environment first:
   - `python3 -m site --user-site`
   - `python3 -m pip show <pkg>` to check whether a package is already installed.
2. Never rerun a failing build in a tight loop. Each failed build is expensive and noisy.
3. Do not launch system-level installer flows as part of a package-install task unless the user approved that broader remediation.
4. Verify the blocker before changing anything. Run environment checks first, then propose exact next steps.
5. For long installs, use `background=true` with `notify_on_complete=true`, but do not start a new install until the previous one is confirmed done.

## Windows-specific constraints
- Do not retry `pip install` purely because a build tool was launched.
- Re-run only after explicit signs that MSVC/build tools are actually installed and available:
  - `where cl.exe`
  - `where link.exe`
  These must both resolve before retry.

### ⚠️ Interpreter mismatch (Warren's Windows machine — 2026-07-24)
On this host `python3` and `pip` can point at DIFFERENT Pythons, so a package
installs but then `python3 -c "import X"` fails with ModuleNotFoundError.

Observed reality:
- `python3` → `C:\Users\khoans\AppData\Local\Microsoft\WindowsApps\python3.exe` = **Python 3.14.5**
- bare `pip` → installs into the Hermes-agent venv = **Python 3.12** (different interpreter)
- Result: `pip install pyodbc` succeeds, but `python3 -c "import pyodbc"` says "No module named 'pyodbc'".

**Fix (always use this form on Warren's machine):**
```
python3 -m pip install <pkg>          # targets the SAME interpreter as `python3`
```
If that still misses (rare), force the target:
```
python3 -m pip install --target "$(python3 -c 'import sysconfig; print(sysconfig.get_paths()["purelib"])')" <pkg>
```

**Verify with the SAME interpreter you will run:**
```
python3 -c "import pyodbc; print(pyodbc.__version__)"
where python3        # confirm which exe `python3` resolves to
```
Do NOT trust a bare `pip show <pkg>` as proof `python3` can import it — they may be
different interpreters. This is a setup-state gotcha, not a broken tool.

## Anti-patterns
- Don't run `winget install rust*` or similar system installs implicitly.
- Don't replace a failed native build with assumptions or placeholder success.