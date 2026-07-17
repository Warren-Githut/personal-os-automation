<#
.SYNOPSIS
    Setup git hooks for Personal OS vault.
.DESCRIPTION
    Creates git hooks that enforce:
    - Pre-commit: Vietnamese diacritics check for .md files
    - Pre-commit: YAML frontmatter validation (if validate-yaml.ps1 exists)
.NOTES
    Run from vault/ directory (where .git exists).
    Requires: PowerShell 5.1+, git, Python 3
    Hooks use #!/bin/sh shebang for Git Bash compatibility on Windows.
    Path calculation: hooks at .git/hooks/<name>, vault root = hooks dir + /../../
#>

$ErrorActionPreference = "Stop"

# -- Detect git root ---------------------------------------------------
$scriptDir = Split-Path -Parent $PSCommandPath
$vaultDir = Resolve-Path "$scriptDir/.."
$gitDir = "$vaultDir/.git"

if (-not (Test-Path $gitDir)) {
    Write-Host "[WARN] No .git directory found at $vaultDir" -ForegroundColor Yellow
    Write-Host "  Initialize git repo first: git init" -ForegroundColor Cyan
    exit 1
}

$hooksDir = "$gitDir/hooks"
if (-not (Test-Path $hooksDir)) {
    New-Item -ItemType Directory -Path $hooksDir -Force | Out-Null
}

Write-Host "`n[Setup] Setting up Personal OS git hooks..." -ForegroundColor Cyan
Write-Host "  Git hooks directory: $hooksDir" -ForegroundColor Gray

# -- 1. PRE-COMMIT HOOK ------------------------------------------------
$preCommitPath = "$hooksDir/pre-commit"
$preCommitLines = @(
    '#!/bin/sh',
    '# Personal OS Pre-Commit Hook',
    '# Runs: diacritics_check.py + validate-yaml.ps1 (if exists)',
    '# Path: hook at .git/hooks/pre-commit, vault root = hooks dir + /../../',
    'HOOK_DIR="$(cd "$(dirname "$0")" && pwd)"',
    'VAULT_DIR="$(cd "$HOOK_DIR/../.." && pwd)"',
    '# ---- 1. Vietnamese Diacritics Check ----',
    'DIACRITICS_SCRIPT="$VAULT_DIR/scripts/diacritics_check.py"',
    'if [ -f "$DIACRITICS_SCRIPT" ]; then',
    '    python "$DIACRITICS_SCRIPT"',
    '    if [ $? -ne 0 ]; then exit 1; fi',
    'else',
    '    echo "[WARN] diacritics_check.py not found at $DIACRITICS_SCRIPT" >&2',
    'fi',
    '# ---- 2. YAML Frontmatter Validation (optional) ----',
    'YAML_SCRIPT="$VAULT_DIR/scripts/validate-yaml.ps1"',
    'if [ -f "$YAML_SCRIPT" ]; then',
    '    powershell.exe -ExecutionPolicy Bypass -NoProfile -File "$YAML_SCRIPT" -StagedOnly',
    '    if [ $? -ne 0 ]; then exit 1; fi',
    'fi'
)
$preCommitContent = $preCommitLines -join "`n"
Set-Content -Path $preCommitPath -Value $preCommitContent -NoNewline
Write-Host "  [OK] Created pre-commit hook: $preCommitPath" -ForegroundColor Green

# -- Summary -----------------------------------------------------------
Write-Host "`n[Info] Setup complete!" -ForegroundColor Green
Write-Host "`n  Active hooks:" -ForegroundColor Cyan
Write-Host "  +----------------------------------------------+" -ForegroundColor Gray
Write-Host "  | pre-commit  -> diacritics_check.py (diacrit.) |" -ForegroundColor White
Write-Host "  |              -> validate-yaml.ps1 (YAML)      |" -ForegroundColor White
Write-Host "  +----------------------------------------------+" -ForegroundColor Gray

Write-Host "`n  [DONE] Hooks registered. They will run on every git commit.`n" -ForegroundColor Green
