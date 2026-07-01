# Kubernetes (raw manifests)

This describes the raw Kubernetes objects in [k8s/](../k8s/) and how to work
with them on the local **kind** cluster `dev`. Everything here reflects the
actual manifests in the repo.

All objects live in the **`kubeops-dev`** namespace and share the label
`app: kubeops`.

## Namespace

[k8s/namespace.yaml](../k8s/namespace.yaml) creates the `kubeops-dev` namespace.
Applying the whole folder (`kubectl apply -f k8s/`) creates it first.

```powershell
kubectl get namespace kubeops-dev
```

## Deployment

[k8s/deployment.yaml](../k8s/deployment.yaml) — name `kubeops`:

- **replicas:** 2
- **image:** `kubeops:local`, `imagePullPolicy: IfNotPresent`
- **containerPort:** 8000 (named `http`)
- **envFrom:** ConfigMap `kubeops-config` + Secret `kubeops-secret`
- **livenessProbe:** `httpGet /health` on 8000 (`initialDelaySeconds: 5`,
  `periodSeconds: 10`)
- **readinessProbe:** `httpGet /ready` on 8000 (same timings)
- **resources:** requests `cpu 100m / memory 128Mi`, limits `cpu 500m / memory 256Mi`
- **securityContext:** `runAsNonRoot: true`, `runAsUser: 1000`,
  `allowPrivilegeEscalation: false`, `readOnlyRootFilesystem: true`

`readOnlyRootFilesystem: true` is safe because the app writes nothing to disk
and `PYTHONDONTWRITEBYTECODE=1` (set in the image) prevents `.pyc` writes.

## Service

[k8s/service.yaml](../k8s/service.yaml) — name `kubeops`, type `ClusterIP`:

- port **80** → targetPort **8000** (named `http`)
- selector `app: kubeops`

## Ingress

[k8s/ingress.yaml](../k8s/ingress.yaml) — name `kubeops`:

- host **`kubeops.local`**, path `/` (`pathType: Prefix`)
- backend service `kubeops` port `80`

An Ingress needs an ingress controller in the cluster to actually route traffic,
and `kubeops.local` needs to resolve to the cluster. On kind that means
installing an ingress controller and adding a hosts entry — otherwise use
`kubectl port-forward` (below), which always works. See
[troubleshooting](troubleshooting.md#ingress-not-working).

## ConfigMap

[k8s/configmap.yaml](../k8s/configmap.yaml) — name `kubeops-config`, non-secret
config consumed via `envFrom`:

- `APP_ENV: "development"`
- `LOG_LEVEL: "INFO"`

## Secret

[k8s/secret.example.yaml](../k8s/secret.example.yaml) — an **example only**. It
defines Secret `kubeops-secret` with a placeholder `APP_SECRET_KEY`.

> The real Secret (`k8s/secret.yaml`) is **gitignored** and never committed.
> Create it from the example:

```powershell
Copy-Item k8s/secret.example.yaml k8s/secret.yaml
# edit k8s/secret.yaml and set a real APP_SECRET_KEY
kubectl apply -f k8s/secret.yaml
```

If you `kubectl apply -f k8s/` before creating the real Secret, the deployment
will apply, but pods will fail to start until Secret `kubeops-secret` exists
(the `envFrom` secretRef is required).

## Probes

- **Liveness** (`/health`): if it fails, Kubernetes restarts the container.
- **Readiness** (`/ready`): if it fails, the pod is removed from Service
  endpoints (no traffic) until it passes.

Both are simple HTTP 200 checks backed by the app. See
[docs/monitoring.md](monitoring.md).

## Resources

Requests are what the scheduler reserves; limits are the hard ceiling. Current
values are modest (suitable for kind): requests `100m` CPU / `128Mi`, limits
`500m` CPU / `256Mi`.

## Deploy and verify

```powershell
# Build and load the image into kind (raw YAML uses kubeops:local):
docker build -t kubeops:local .
kind load docker-image kubeops:local --name dev

# Create the real Secret (see above), then apply everything:
kubectl apply -f k8s/

kubectl get pods,svc,ingress -n kubeops-dev
kubectl rollout status deployment/kubeops -n kubeops-dev

# Reach the app without an ingress controller:
kubectl port-forward svc/kubeops 8000:80 -n kubeops-dev
curl http://localhost:8000/health
```

Or use the helper scripts: [scripts/deploy-k8s.ps1](../scripts/deploy-k8s.ps1),
[scripts/check-health.ps1](../scripts/check-health.ps1),
[scripts/port-forward.ps1](../scripts/port-forward.ps1),
[scripts/cleanup.ps1](../scripts/cleanup.ps1).

## Useful kubectl commands

```powershell
kubectl get all -n kubeops-dev                       # everything in the namespace
kubectl get pods -n kubeops-dev -o wide              # pods + node/IP
kubectl describe deployment kubeops -n kubeops-dev   # rollout details/events
kubectl describe pod <pod> -n kubeops-dev            # why a pod isn't Ready
kubectl logs -f deployment/kubeops -n kubeops-dev    # follow logs (stdout)
kubectl get events -n kubeops-dev --sort-by=.lastTimestamp
kubectl exec -it <pod> -n kubeops-dev -- sh          # shell into a pod
kubectl rollout restart deployment/kubeops -n kubeops-dev
kubectl delete -f k8s/                               # tear down raw resources
```
