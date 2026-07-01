# Monitoring

This folder documents the monitoring story for KubeOps. **What exists today** is
health/readiness endpoints, stdout logs, and Kubernetes probes. Metrics
dashboards (Prometheus/Grafana) are a **future** step — there is no `/metrics`
endpoint and no monitoring stack deployed by this repo yet.

For the operational side (logs, describe, events, probe behavior), see
[../docs/monitoring.md](../docs/monitoring.md).

## What's implemented now

| Signal            | Source                          | How to see it                              |
| ----------------- | ------------------------------- | ------------------------------------------ |
| Liveness          | `GET /health`                   | probe restarts container; `curl /health`   |
| Readiness         | `GET /ready`                    | probe gates traffic; `curl /ready`         |
| Application logs  | stdout (structured text)        | `kubectl logs -f deployment/kubeops -n kubeops-dev` |
| Pod/probe events  | Kubernetes events               | `kubectl describe pod <pod> -n kubeops-dev`|

Quick health check: [../scripts/check-health.ps1](../scripts/check-health.ps1).

## Future: Prometheus + Grafana

This is a plan, not something shipped here. Suggested steps:

1. **Expose metrics** — add a `/metrics` endpoint to the FastAPI app, e.g. with
   [`prometheus-fastapi-instrumentator`](https://github.com/trallnag/prometheus-fastapi-instrumentator),
   which publishes request count, latency histograms, and in-progress requests.
2. **Deploy the stack** — install `kube-prometheus-stack` (Prometheus, Grafana,
   Alertmanager) via Helm into a `monitoring` namespace.
3. **Scrape the app** — add a `ServiceMonitor` (or Prometheus scrape
   annotations) so Prometheus discovers the `kubeops` Service.
4. **Visualize** — build a small Grafana dashboard (see
   [grafana-dashboard-notes.md](grafana-dashboard-notes.md)).

## Suggested alerts (future)

- Pod restart rate elevated (CrashLoop signal).
- Readiness failing / endpoints at zero.
- p95 latency above a threshold.
- 5xx error rate above a threshold.

## Screenshots

Capture **real** screenshots once monitoring is running and store them under
[../docs/screenshots/](../docs/screenshots/) — see
[../docs/screenshots/README.md](../docs/screenshots/README.md) for the list and
filenames. Do not add fake/placeholder dashboards.
