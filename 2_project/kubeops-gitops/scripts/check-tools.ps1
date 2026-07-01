# check-tools.ps1
# Prints the versions and status of every tool this project needs.
# Read-only: this script does NOT change anything on your machine.

# Keep going even if one tool is missing, so you see the full picture.
$ErrorActionPreference = "Continue"

Write-Host "=== KubeOps tool check ===" -ForegroundColor Cyan
Write-Host ""

# Helper: run a command and report a clear PASS/FAIL line for it.
function Invoke-Check {
    param(
        [string]$Label,     # Friendly name shown to the user
        [scriptblock]$Action # The command to run
    )

    Write-Host ">>> $Label" -ForegroundColor Yellow
    try {
        & $Action
        if ($LASTEXITCODE -ne $null -and $LASTEXITCODE -ne 0) {
            Write-Host "    [FAIL] '$Label' returned exit code $LASTEXITCODE" -ForegroundColor Red
        } else {
            Write-Host "    [OK] $Label" -ForegroundColor Green
        }
    }
    catch {
        Write-Host "    [FAIL] $Label - $($_.Exception.Message)" -ForegroundColor Red
    }
    Write-Host ""
}

Invoke-Check "docker --version"            { docker --version }
Invoke-Check "docker ps"                   { docker ps }
Invoke-Check "kubectl version --client"    { kubectl version --client }
Invoke-Check "kind version"                { kind version }
Invoke-Check "helm version"                { helm version }
Invoke-Check "kubectl config current-context" { kubectl config current-context }
Invoke-Check "kubectl get nodes"           { kubectl get nodes }

Write-Host "=== Tool check finished ===" -ForegroundColor Cyan
Write-Host "If any line above says [FAIL], fix that tool before continuing." -ForegroundColor Cyan
