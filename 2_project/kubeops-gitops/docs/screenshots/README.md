# Screenshots

This folder is intentionally empty of images for now. **No fake or placeholder
screenshots** are committed — the point of this project is to be honest about
what has actually been run.

When you run the project locally, capture **real** screenshots and save them here
using the filenames below, then reference them from the README/docs.

## Screenshots to capture

| Filename                     | What to capture                                                        |
| ---------------------------- | --------------------------------------------------------------------- |
| `01-tests-passing.png`       | `python -m pytest` output with all tests passing                      |
| `02-docker-run-health.png`   | container running + `curl http://localhost:8000/health` returning `{"status":"ok"}` |
| `03-swagger-docs.png`        | FastAPI interactive docs at `http://localhost:8000/docs`              |
| `04-kubectl-get-all.png`     | `kubectl get all -n kubeops-dev` with pods `Running`/`Ready`          |
| `05-port-forward-health.png` | `kubectl port-forward` + `/health` working against the cluster        |
| `06-helm-list.png`           | `helm list -n kubeops-dev` showing the deployed release               |
| `07-argocd-app.png`          | the Argo CD `kubeops` Application (Synced/Healthy) — after you install Argo CD |
| `08-ci-pipeline.png`         | a green GitHub Actions run — after you commit the workflows           |
| `09-grafana-dashboard.png`   | the Grafana dashboard — after you add metrics + the monitoring stack  |

## Tips

- Crop to the relevant terminal/window; keep them readable.
- Don't stage or doctor output. If something isn't built yet (Argo CD, CI,
  Grafana), simply capture that screenshot later when it genuinely works.
- Prefer PNG for crisp text.
