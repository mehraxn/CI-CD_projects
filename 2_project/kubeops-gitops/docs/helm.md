# Helm

The Helm chart in [helm/kubeops/](../helm/kubeops/) packages the same objects as
the raw manifests, but configurable through values. This matches the actual
chart in the repo.

## Chart structure

```text
helm/kubeops/
├── Chart.yaml            # name: kubeops, version 0.1.0, appVersion 0.1.0
├── values.yaml           # default values
├── values-dev.yaml       # dev overrides (kind)
├── values-prod.yaml      # prod-shaped overrides (example)
└── templates/
    ├── _helpers.tpl      # name/label/serviceAccount/secret helpers
    ├── deployment.yaml   # Deployment
    ├── service.yaml      # ClusterIP Service
    ├── ingress.yaml      # Ingress (if ingress.enabled)
    ├── configmap.yaml    # env → ConfigMap
    ├── secret.yaml       # rendered Secret (if secret.create)
    └── serviceaccount.yaml  # ServiceAccount (if serviceAccount.create)
```

Object names come from `_helpers.tpl`. With release name `kubeops`, the
fullname is `kubeops`, so you get Service/Deployment `kubeops`, ConfigMap
`kubeops-config`, and Secret `kubeops-secret` — matching the raw manifests.

## Values files

`values.yaml` (defaults) exposes:

| Key                         | Default                         | Purpose                              |
| --------------------------- | ------------------------------- | ------------------------------------ |
| `replicaCount`              | `2`                             | number of pods                       |
| `image.repository`          | `kubeops`                       | image name                           |
| `image.tag`                 | `local`                         | image tag                            |
| `image.pullPolicy`          | `IfNotPresent`                  | pull policy                          |
| `service.type` / `.port` / `.targetPort` | `ClusterIP` / `80` / `8000` | Service shape             |
| `ingress.enabled` / `.host` / `.path` | `true` / `kubeops.local` / `/` | Ingress             |
| `env`                       | `APP_ENV`, `LOG_LEVEL`          | rendered into the ConfigMap          |
| `secret.create`             | `true`                          | render a Secret vs. use an existing  |
| `secret.existingSecret`     | `""`                            | name to use when `create: false`     |
| `secret.values.APP_SECRET_KEY` | placeholder                  | rendered secret value (override!)    |
| `containerPort`             | `8000`                          | container port                       |
| `probes.liveness/readiness` | `/health` / `/ready`            | probe paths + timings                |
| `resources`                 | 100m/128Mi → 500m/256Mi         | requests/limits                      |
| `securityContext`           | non-root, RO rootfs             | pod hardening                        |
| `serviceAccount.create`     | `true`                          | create a ServiceAccount              |

**`values-dev.yaml`** (local kind): `image.tag: local`, `LOG_LEVEL: DEBUG`,
ingress host `kubeops.local`.

**`values-prod.yaml`** (example / aspirational): 3 replicas, image
`ghcr.io/mehraxn/kubeops:latest`, ingress class `nginx`, host
`kubeops.example.com`, and `secret.create: false` with
`existingSecret: kubeops-secret` (provision the secret out-of-band). The GHCR
image referenced here is **not published yet** because CI/CD isn't wired up.

## Install

```powershell
# Ensure the dev image exists in kind first:
docker build -t kubeops:local .
kind load docker-image kubeops:local --name dev

helm lint ./helm/kubeops
helm template kubeops ./helm/kubeops -f helm/kubeops/values-dev.yaml   # preview YAML
helm install kubeops ./helm/kubeops -n kubeops-dev --create-namespace -f helm/kubeops/values-dev.yaml

kubectl get pods,svc -n kubeops-dev
```

Or run [scripts/deploy-helm.ps1](../scripts/deploy-helm.ps1), which lints then
does `helm upgrade --install` and shows the result.

## Upgrade

```powershell
helm upgrade kubeops ./helm/kubeops -n kubeops-dev -f helm/kubeops/values-dev.yaml
# override a single value inline:
helm upgrade kubeops ./helm/kubeops -n kubeops-dev -f helm/kubeops/values-dev.yaml --set replicaCount=3
```

`helm upgrade --install` (used by the script) installs on first run and upgrades
afterward, so it is safe to run repeatedly.

## Rollback

```powershell
helm history kubeops -n kubeops-dev          # list revisions
helm rollback kubeops 1 -n kubeops-dev       # roll back to revision 1
helm status kubeops -n kubeops-dev
```

## Uninstall

```powershell
helm uninstall kubeops -n kubeops-dev
```

This removes the chart's objects but leaves the namespace. Use
[scripts/cleanup.ps1](../scripts/cleanup.ps1) to also (optionally) delete the
namespace with `-DeleteNamespace`.

## Notes

- The Secret and Ingress templates are conditional. Set `secret.create: false`
  + `secret.existingSecret: <name>` to use a pre-provisioned Secret;
  set `ingress.enabled: false` to skip the Ingress.
- Never commit real secret values into a values file. `values.yaml` ships an
  obvious placeholder; override it per environment.
