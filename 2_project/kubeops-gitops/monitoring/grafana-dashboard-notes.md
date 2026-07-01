# Grafana Dashboard Notes (future)

There is **no Grafana dashboard JSON in this repo yet** — this file is a design
note for when a `/metrics` endpoint and the Prometheus/Grafana stack are added
(see [README.md](README.md)). Nothing here is live.

## Prerequisites (not done yet)

1. A `/metrics` endpoint on the app (e.g. `prometheus-fastapi-instrumentator`).
2. Prometheus scraping the `kubeops` Service (via `ServiceMonitor` or scrape
   annotations).
3. Grafana with Prometheus as a data source.

## Panels to build

A small, honest dashboard for a single service:

| Panel                     | Idea / example query (PromQL)                                             |
| ------------------------- | ------------------------------------------------------------------------ |
| Request rate (req/s)      | `sum(rate(http_requests_total{job="kubeops"}[5m]))`                      |
| Error rate (5xx)          | `sum(rate(http_requests_total{job="kubeops",status=~"5.."}[5m]))`       |
| Latency p95               | `histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket{job="kubeops"}[5m])) by (le))` |
| In-progress requests      | `sum(http_requests_in_progress{job="kubeops"})`                          |
| Pod restarts              | `sum(kube_pod_container_status_restarts_total{namespace="kubeops-dev"})`|
| Ready replicas            | `kube_deployment_status_replicas_available{deployment="kubeops"}`        |
| CPU / memory usage        | `container_cpu_usage_seconds_total` / `container_memory_working_set_bytes` (filtered to the pods) |

> Exact metric names depend on the instrumentation library and the
> kube-state-metrics / cAdvisor exporters you install. Adjust labels/metric names
> to match your actual setup before saving a dashboard.

## Suggested layout

- **Row 1 — Traffic:** request rate, error rate, latency p95.
- **Row 2 — Health:** ready replicas, pod restarts, in-progress requests.
- **Row 3 — Resources:** CPU usage vs. limit, memory usage vs. limit.

## When you export a dashboard

1. Build it in the Grafana UI.
2. **Share → Export → Save to file** to get the dashboard JSON.
3. Commit it here as `grafana-dashboard-notes.json` (or similar) and link it from
   [README.md](README.md).
4. Capture a **real** screenshot into
   [../docs/screenshots/](../docs/screenshots/) (see its
   [README](../docs/screenshots/README.md)).
