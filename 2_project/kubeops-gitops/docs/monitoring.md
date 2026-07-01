# Monitoring & Observability

What's actually available today is **health/readiness endpoints + stdout logs +
Kubernetes probes**. Metrics dashboards (Prometheus/Grafana) are a documented
future step, not something shipped in this repo.

## Health and readiness endpoints

The app exposes two simple checks (see [app/main.py](../app/main.py)):

| Endpoint  | Response              | Used by                          |
| --------- | --------------------- | -------------------------------- |
| `/health` | `{"status":"ok"}`     | liveness probe / uptime checks   |
| `/ready`  | `{"status":"ready"}`  | readiness probe / traffic gating |

Both return HTTP 200 when the app is up. Because storage is in-memory and has no
external dependencies, `/ready` currently reflects "the process is serving,"
not "a database is reachable."

Quick check via port-forward:

```powershell
kubectl port-forward svc/kubeops 8000:80 -n kubeops-dev
curl http://localhost:8000/health
curl http://localhost:8000/ready
```

Or run [scripts/check-health.ps1](../scripts/check-health.ps1), which
port-forwards, calls `/health`, prints PASS/FAIL, and cleans up.

## Kubernetes probes

The Deployment wires these endpoints to probes (see
[docs/kubernetes.md](kubernetes.md#probes)):

- **livenessProbe** → `GET /health`. On failure, the container is restarted.
- **readinessProbe** → `GET /ready`. On failure, the pod is pulled from Service
  endpoints until it passes.

Both use `initialDelaySeconds: 5`, `periodSeconds: 10`.

## Logs

The app logs to **stdout** (configured in `app/main.py`), so standard Kubernetes
log tooling works:

```powershell
kubectl logs -f deployment/kubeops -n kubeops-dev        # follow all replicas' logs
kubectl logs <pod> -n kubeops-dev                        # a single pod
kubectl logs <pod> -n kubeops-dev --previous             # logs from a crashed container
```

Log verbosity is controlled by `LOG_LEVEL` (`INFO` by default, `DEBUG` in
`values-dev.yaml`).

## Describe & events

For "why isn't this healthy?" questions:

```powershell
kubectl describe pod <pod> -n kubeops-dev                # events, probe failures, restarts
kubectl describe deployment kubeops -n kubeops-dev       # rollout status
kubectl get events -n kubeops-dev --sort-by=.lastTimestamp
```

See [docs/troubleshooting.md](troubleshooting.md) for interpreting common
states (`CrashLoopBackOff`, `ImagePullBackOff`, not Ready, etc.).

## Prometheus / Grafana (future / optional)

Not implemented yet. There is **no `/metrics` endpoint** today. The intended
path is documented in [monitoring/README.md](../monitoring/README.md) and
[monitoring/grafana-dashboard-notes.md](../monitoring/grafana-dashboard-notes.md):

1. add a `/metrics` endpoint (e.g. `prometheus-fastapi-instrumentator`),
2. deploy `kube-prometheus-stack` (Prometheus + Grafana) via Helm,
3. scrape the app (ServiceMonitor / annotations),
4. build a small Grafana dashboard (request rate, latency, error rate, restarts).

## Screenshots to add later

Do not fake screenshots. When you run this locally, capture real ones and place
them under [docs/screenshots/](screenshots/). The suggested list and filenames
are in [docs/screenshots/README.md](screenshots/README.md).
