---
name: windows-toolchain-install-verification
description: "For Windows: do not treat winget/pip installer runs as success. Verify build toolchain with concrete evidence before retrying."
version: 0.1.0
author: Hermes Agent + Warren
license: MIT
platforms: [windows]
---

# Windows Toolchain Install Verification

## Trigger
Any of the following:
- `winget install Microsoft.VisualStudio.2022.BuildTools` or Build Tools installer
- `pip install` failing with `link.exe`, `link: extra operand`, `maturin failed`, `Microsoft Visual C++ 14.0 or greater is required`, `rustc`
- Any pip package with Rust/C/C++ extension on Windows builds failing despite installer/silent flags

## Rule
Never assume success. Installer command returning quickly or showing progress != installed component ready for compiler consumers.

## Minimum Verification Sequence
After a Build Tools install output, confirm ALL of:
1. `where cl.exe` returns a path ending in `VC\Tools\MSVC\<version>\bin\Hostx64\x64\cl.exe`
2. `where link.exe` returns a path from the same MSVC toolset directory
3. `cl.exe` runs and prints a version banner (version/date)
4. If rustup exists: `cargo --version` and `rustc --version` print usable versions

Do not rerun `pip install` until at least 1 and 2 pass.

## Language for user
- Non-IT: state root cause first, then 3 plain options, then ask which to do.
- IT: call out exact missing workload and commands to rerun vs. manual GUI path.
