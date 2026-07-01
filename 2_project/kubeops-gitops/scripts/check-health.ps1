# check-health.ps1
# Starts a temporary port-forward to the kubeops service, calls GET /health,
# prints a clear PASS or FAIL, and then always cleans up the port-forward.

$ErrorActionPreference = "Stop"

$namespace  = "kubeops-dev"
$service    = "svc/kubeops"
$localPort  = 8000
$remotePort = 80
$healthUrl  = "http://localhost:$localPort/health"

Write-Host "=== KubeOps health check ===" -ForegroundColor Cyan

# Start the port-forward as a BACKGROUND process so this script can keep going.
Write-Host "Starting port-forward ($service $localPort`:$remotePort -n $namespace)..." -ForegroundColor Yellow
$pf = Start-Process -FilePath "kubectl" `
    -ArgumentList "port-forward", $service, "$localPort`:$remotePort", "-n", $namespace `
    -PassThru -NoNewWindow

# We use try/finally so the port-forward is ALWAYS stopped, even on error.
try {
    # Give the port-forward a few tries to come up before we call /health.
    $healthy = $false
    for ($i = 1; $i -le 10; $i++) {
        Start-Sleep -Seconds 1
        try {
            $resp = Invoke-WebRequest -Uri $healthUrl -UseBasicParsing -TimeoutSec 3
            if ($resp.StatusCode -eq 200) {
                $healthy = $true
                break
            }
        }
        catch {
            # Not ready yet — keep retrying quietly.
        }
    }

    Write-Host ""
    if ($healthy) {
        Write-Host "[PASS] $healthUrl returned 200 OK" -ForegroundColor Green
        Write-Host "Response body: $($resp.Content)" -ForegroundColor Green
        $exitCode = 0
    }
    else {
        Write-Host "[FAIL] Could not get a 200 from $healthUrl" -ForegroundColor Red
        Write-Host "Is the deployment running? Try: kubectl get pods -n $namespace" -ForegroundColor Red
        $exitCode = 1
    }
}
finally {
    # Always clean up the background port-forward.
    Write-Host ""
    Write-Host "Cleaning up port-forward..." -ForegroundColor Yellow
    if ($pf -and -not $pf.HasExited) {
        Stop-Process -Id $pf.Id -Force -ErrorAction SilentlyContinue
    }
    Write-Host "[OK] Port-forward stopped." -ForegroundColor Green
}

exit $exitCode
