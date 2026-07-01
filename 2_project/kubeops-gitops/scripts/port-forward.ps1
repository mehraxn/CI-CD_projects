# port-forward.ps1
# Forwards the kubeops service to your local machine so you can open it in a
# browser or with curl. This runs in the FOREGROUND and stays open until you
# press Ctrl+C to stop it.
#
# After it starts, open:  http://localhost:8000/health

$ErrorActionPreference = "Stop"

$namespace  = "kubeops-dev"
$service    = "svc/kubeops"
$localPort  = 8000
$remotePort = 80

Write-Host "=== Port-forwarding $service to localhost:$localPort ===" -ForegroundColor Cyan
Write-Host "Open http://localhost:$localPort/health in your browser." -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop." -ForegroundColor Yellow
Write-Host ""

# This command blocks until you stop it with Ctrl+C.
kubectl port-forward $service "$localPort`:$remotePort" -n $namespace
