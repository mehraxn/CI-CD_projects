# cleanup.ps1
# Tears down what this project deployed, in a SAFE order.
#
#   - Uninstalls the Helm release "kubeops" (if it exists)
#   - Deletes the raw k8s/ resources (if they exist)
#   - Optionally deletes the kubeops-dev namespace   (pass -DeleteNamespace)
#   - Optionally deletes the kind cluster "dev"       (pass -DeleteCluster)
#
# By default it NEVER deletes the namespace or the kind cluster.
#
# Examples:
#   .\cleanup.ps1                                  # remove app resources only
#   .\cleanup.ps1 -DeleteNamespace                 # also delete the namespace
#   .\cleanup.ps1 -DeleteNamespace -DeleteCluster  # also delete the kind cluster

param(
    [switch]$DeleteNamespace,
    [switch]$DeleteCluster
)

# Don't stop on the first error: cleanup should try every step.
$ErrorActionPreference = "Continue"

$releaseName = "kubeops"
$namespace   = "kubeops-dev"
$clusterName = "dev"

$k8sDir = Join-Path $PSScriptRoot "..\k8s"

Write-Host "=== KubeOps cleanup ===" -ForegroundColor Cyan

# 1) Uninstall the Helm release if it is installed.
Write-Host ""
Write-Host ">>> Checking for Helm release '$releaseName'..." -ForegroundColor Yellow
$releases = helm list -n $namespace -q 2>$null
if ($releases -contains $releaseName) {
    helm uninstall $releaseName -n $namespace
    Write-Host "[OK] Helm release '$releaseName' uninstalled." -ForegroundColor Green
}
else {
    Write-Host "[SKIP] No Helm release '$releaseName' found." -ForegroundColor DarkGray
}

# 2) Delete raw k8s/ resources if the manifests are present.
Write-Host ""
Write-Host ">>> Deleting raw k8s/ resources (if any)..." -ForegroundColor Yellow
if (Test-Path $k8sDir) {
    # --ignore-not-found so this is quiet when nothing is there.
    kubectl delete -f $k8sDir --ignore-not-found
    Write-Host "[OK] Raw resources removed (any that existed)." -ForegroundColor Green
}
else {
    Write-Host "[SKIP] Manifests folder not found at $k8sDir." -ForegroundColor DarkGray
}

# 3) Optionally delete the namespace.
Write-Host ""
if ($DeleteNamespace) {
    Write-Host ">>> Deleting namespace '$namespace'..." -ForegroundColor Yellow
    kubectl delete namespace $namespace --ignore-not-found
    Write-Host "[OK] Namespace '$namespace' deleted (if it existed)." -ForegroundColor Green
}
else {
    Write-Host "[SKIP] Namespace '$namespace' kept. Pass -DeleteNamespace to remove it." -ForegroundColor DarkGray
}

# 4) Optionally delete the kind cluster (explicit opt-in only).
Write-Host ""
if ($DeleteCluster) {
    Write-Host ">>> Deleting kind cluster '$clusterName'..." -ForegroundColor Yellow
    kind delete cluster --name $clusterName
    Write-Host "[OK] Kind cluster '$clusterName' deleted." -ForegroundColor Green
}
else {
    Write-Host "[SKIP] Kind cluster '$clusterName' kept. Pass -DeleteCluster to remove it." -ForegroundColor DarkGray
}

Write-Host ""
Write-Host "=== Cleanup finished ===" -ForegroundColor Cyan
