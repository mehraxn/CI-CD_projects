# deploy-k8s.ps1
# Deploys the RAW Kubernetes manifests from the k8s/ folder, then shows what
# was created. Use this to try Kubernetes without Helm.

$ErrorActionPreference = "Stop"

$namespace = "kubeops-dev"

# Resolve the k8s/ folder relative to THIS script, so the script works no
# matter what directory you run it from. ($PSScriptRoot = scripts/ folder)
$k8sDir = Join-Path $PSScriptRoot "..\k8s"

if (-not (Test-Path $k8sDir)) {
    Write-Host "[FAIL] Could not find manifests folder at: $k8sDir" -ForegroundColor Red
    exit 1
}

Write-Host "=== Applying raw Kubernetes manifests from k8s/ ===" -ForegroundColor Cyan
kubectl apply -f $k8sDir
if ($LASTEXITCODE -ne 0) {
    Write-Host "[FAIL] 'kubectl apply' failed. Check the errors above." -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Manifests applied." -ForegroundColor Green

# Show the resources created in the kubeops-dev namespace.
Write-Host ""
Write-Host "=== Pods in $namespace ===" -ForegroundColor Cyan
kubectl get pods -n $namespace

Write-Host ""
Write-Host "=== Services in $namespace ===" -ForegroundColor Cyan
kubectl get svc -n $namespace

Write-Host ""
Write-Host "=== Ingress in $namespace ===" -ForegroundColor Cyan
kubectl get ingress -n $namespace

Write-Host ""
Write-Host "Tip: pods may take a few seconds to become Running/Ready." -ForegroundColor Cyan
