$ErrorActionPreference = "Stop"

$VaultPath = "C:\Users\khoans\Documents\Personal_OS\personal_vault"
$Branch = "main"
$LogFile = Join-Path $env:USERPROFILE "personal_os_git_sync.log"

function Write-Log {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Add-Content -Path $LogFile -Value "[$timestamp] $Message"
}

try {
    Set-Location $VaultPath

    git add -A

    git diff --cached --quiet
    if ($LASTEXITCODE -eq 0) {
        Write-Log "No changes to commit."
        exit 0
    }

    $message = "vault backup: $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
    git commit -m $message | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Log "Commit failed."
        exit 1
    }

    git pull --rebase origin $Branch | Out-Null
    if ($LASTEXITCODE -ne 0) {
        git rebase --abort | Out-Null
        Write-Log "Pull/rebase failed after commit. Manual check needed."
        exit 1
    }

    git push origin $Branch | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Log "Push failed."
        exit 1
    }

    Write-Log "Committed and pushed successfully."
    exit 0
}
catch {
    Write-Log "Error: $($_.Exception.Message)"
    exit 1
}
