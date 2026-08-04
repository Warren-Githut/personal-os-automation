---
name: windows-native-build-troubleshooting
description: Troubleshoot Windows build failures for Python packages with native extensions, especially MSVC/Rust/maturin and hnswlib-class issues.
---

# Windows Native Build Troubleshooting

## Purpose
Compact, repeatable guidance when a `pip install` fails on Windows due to native build toolchain issues (MSVC, `cl.exe`, `link.exe`, Rust `maturin`).

## When to use
- `pip install` of a package with native extensions fails with `link.exe` errors.
- Errors reference `Microsoft Visual C++ 14.0 or greater is required`.
- Build logs show `maturin failed`, `cargo ... rustc`, or `link: extra operand`.

## Quick checklist
1. Confirm `link.exe` exists: `where link.exe`.
2. Confirm `cl.exe` exists: `where cl.exe`.
3. If either is missing, install **Visual Studio Build Tools 2022**:
   - Workload: **Desktop development with C++**
   - Also select a matching Windows SDK if prompted.
4. Reopen shell/tab so `vcvarsall` environment is loaded, or rerun from a fresh terminal.
5. Retry pip install in the same Python environment where it failed initially.
6. If `hnswlib` still fails after MSVC is present, retry with `pip install --no-build-isolation hnswlib` as a fallback.

## Provenance note
This class of failure is environmental, not a durable agent constraint. Do not encode “tool X does not work on Windows” — encode the *fix* instead.

## Anti-patterns
- Do not run follow-up `winget install rust*` or other system-level installs unless the user has explicitly approved a broader remediation beyond the original task. After a blocker, prefer proposing the fix, not launching unattended system changes.
- Do not rerun the failing pip install in a tight loop. Each failed build is expensive and noisy.