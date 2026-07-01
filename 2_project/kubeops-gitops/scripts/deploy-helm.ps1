# deploy-helm.ps1
# Lints the Helm chart, then installs it (or upgrades it if already installed)
# using the dev values. Finally shows the pods and service.
# "install or upgrade" is done with a single `helm upgrade --install` command.

$ErrorActionPreference = "Stop"

$releaseName = "kubeops"
$namespace   = "kubeops-dev"

# Resolve the chart folder relative to this script.
$chartDir   = Join-Path $PSScriptRoot "..\helm\kubeops"
$valuesFile = Join-Path $chartDir "values-dev.yaml"

if (-not (Test-Path $chartDir)) {
    Write-Host "[FAIL] Could not find chart at: $chartDir" -ForegroundColor Red
    exit 1
}

# 1) Lint the chart to catch template mistakes early.
Write-Host "=== helm lint ===" -ForegroundColor Cyan
helm lint $chartDir
if ($LASTEXITCODE -ne 0) {
    Write-Host "[FAIL] helm lint reported problems. Fix them before deploying." -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Chart passed lint." -ForegroundColor Green

# 2) Install or upgrade the release.
Write-Host ""
Write-Host "=== helm upgrade --install '$releaseName' ===" -ForegroundColor Cyan
helm upgrade --install $releaseName $chartDir `
    --namespace $namespace `
    --create-namespace `
    --values $valuesFile
if ($LASTEXITCODE -ne 0) {
    Write-Host "[FAIL] helm upgrade/install failed. Check the errors above." -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Release '$releaseName' is deployed." -ForegroundColor Green

# 3) Show what is running.
Write-Host ""
Write-Host "=== Pods in $namespace ===" -ForegroundColor Cyan
kubectl get pods -n $namespace

Write-Host ""
Write-Host "=== Service in $namespace ===" -ForegroundColor Cyan
kubectl get svc -n $namespace

Write-Host ""
Write-Host "Tip: run scripts/check-health.ps1 to verify /health responds." -ForegroundColor Cyan
