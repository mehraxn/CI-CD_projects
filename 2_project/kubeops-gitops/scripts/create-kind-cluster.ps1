# create-kind-cluster.ps1
# Creates the local kind cluster "dev" ONLY if it does not already exist.
# Safe to run repeatedly: it will never destroy or recreate an existing cluster.

$ErrorActionPreference = "Stop"

$clusterName = "dev"
$contextName = "kind-dev"

Write-Host "=== Ensuring kind cluster '$clusterName' exists ===" -ForegroundColor Cyan

# Ask kind for the list of existing clusters.
$existing = kind get clusters 2>$null

if ($existing -contains $clusterName) {
    Write-Host "[OK] Cluster '$clusterName' already exists. Nothing to create." -ForegroundColor Green
}
else {
    Write-Host "Cluster '$clusterName' not found. Creating it now..." -ForegroundColor Yellow
    kind create cluster --name $clusterName
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[FAIL] Failed to create kind cluster '$clusterName'." -ForegroundColor Red
        exit 1
    }
    Write-Host "[OK] Cluster '$clusterName' created." -ForegroundColor Green
}

# Point kubectl at the kind cluster.
Write-Host ""
Write-Host "Setting kubectl context to '$contextName'..." -ForegroundColor Yellow
kubectl config use-context $contextName
if ($LASTEXITCODE -ne 0) {
    Write-Host "[FAIL] Could not switch to context '$contextName'." -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Context set to '$contextName'." -ForegroundColor Green

# Show the nodes so you can confirm the cluster is up.
Write-Host ""
Write-Host "Cluster nodes:" -ForegroundColor Cyan
kubectl get nodes
