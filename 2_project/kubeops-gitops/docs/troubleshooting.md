# Troubleshooting

Common problems when running KubeOps locally, with concrete fixes. Commands are
PowerShell-friendly (Windows). Namespace is `kubeops-dev` throughout.

Run [scripts/check-tools.ps1](../scripts/check-tools.ps1) first — it verifies
Docker, kubectl, kind, Helm, your context, and nodes in one shot.

---

## Docker not running

**Symptom:** `error during connect` / `docker ps` fails / the kind node isn't
listed.

**Fix:** start **Docker Desktop** and wait until it reports "running", then:

```powershell
docker ps        # should list dev-control-plane when kind is up
```

## kind cluster missing

**Symptom:** `kubectl` errors like `connection refused`, or `kind get clusters`
doesn't list `dev`.

**Fix:**

```powershell
kind get clusters
# if 'dev' is missing:
.\scripts\create-kind-cluster.ps1     # creates 'dev' only if absent, sets context
```

## Wrong kubectl context

**Symptom:** commands target the wrong cluster; `kubectl get nodes` shows
unexpected nodes.

**Fix:**

```powershell
kubectl config current-context        # expect: kind-dev
kubectl config use-context kind-dev
```

## ImagePullBackOff / ErrImagePull

**Symptom:** pods stuck in `ImagePullBackOff`.

**Cause:** the image isn't available to the cluster. The dev setup uses
`kubeops:local`, which is a **local** image — kind can't pull it from a registry.

**Fix:** build it and load it into kind:

```powershell
docker build -t kubeops:local .
kind load docker-image kubeops:local --name dev
kubectl rollout restart deployment/kubeops -n kubeops-dev
```

For the prod values (`ghcr.io/mehraxn/kubeops`), the image must actually exist in
GHCR and be pullable (public, or an `imagePullSecret` configured). Note that
image isn't published yet — CI isn't wired up.

## CrashLoopBackOff

**Symptom:** pod starts, exits, restarts repeatedly.

**Fix:** read the logs — the app logs to stdout:

```powershell
kubectl logs <pod> -n kubeops-dev
kubectl logs <pod> -n kubeops-dev --previous     # last crashed container
kubectl describe pod <pod> -n kubeops-dev        # events at the bottom
```

Common cause here: the required Secret `kubeops-secret` is missing (the
Deployment uses `envFrom` on it). Create it — see
[kubernetes.md → Secret](kubernetes.md#secret).

## Pod not Ready (0/1 or 1/2)

**Symptom:** pod is `Running` but not `Ready`; Service has no endpoints.

**Cause:** the **readiness** probe (`/ready`) isn't passing yet.

**Fix:**

```powershell
kubectl describe pod <pod> -n kubeops-dev        # look for "Readiness probe failed"
kubectl get endpoints kubeops -n kubeops-dev     # should list pod IPs once Ready
```

Give it a few seconds (`initialDelaySeconds: 5`). If it never becomes Ready,
check logs for a startup error.

## Service not reachable

**Symptom:** `curl` to the service fails.

**Fix:** confirm the Service has endpoints (pods must be Ready), then use
port-forward:

```powershell
kubectl get svc,endpoints -n kubeops-dev
kubectl port-forward svc/kubeops 8000:80 -n kubeops-dev
curl http://localhost:8000/health
```

## port-forward fails

**Symptom:** `port-forward` exits immediately or "address already in use".

**Fix:**

- Another process is on port 8000 — stop it or forward to a different local port:
  `kubectl port-forward svc/kubeops 8081:80 -n kubeops-dev`.
- The pod isn't Ready yet — wait for `READY 1/1` (see "Pod not Ready").
- On Windows, a stray `kubectl` may hold the port; close old terminals or:
  `Get-Process kubectl | Stop-Process`.

## Ingress not working

**Symptom:** `http://kubeops.local` doesn't resolve or returns nothing.

**Cause:** an Ingress object alone does nothing without an **ingress controller**,
and `kubeops.local` must resolve to the cluster.

**Fix (either):**

- **Easiest:** skip ingress and use `kubectl port-forward` (always works).
- **Full setup:** install an ingress controller (e.g. ingress-nginx for kind),
  then add a hosts entry mapping `kubeops.local` to `127.0.0.1` in
  `C:\Windows\System32\drivers\etc\hosts` (edit as Administrator).

## Helm install fails

**Symptom:** `helm install`/`upgrade` errors.

**Fix:**

```powershell
helm lint ./helm/kubeops                          # catch template errors
helm template kubeops ./helm/kubeops -f helm/kubeops/values-dev.yaml   # render locally
```

- "cannot re-use a name that is still in use" → the release already exists; use
  `helm upgrade` (or [scripts/deploy-helm.ps1](../scripts/deploy-helm.ps1), which
  does `upgrade --install`).
- Namespace missing → add `--create-namespace`.
- `secret.existingSecret is required` → you set `secret.create: false` without
  providing `existingSecret`.

## Argo CD OutOfSync

**Symptom:** the `kubeops` Application shows **OutOfSync**.

**Cause (expected):** manual sync is the default, so Argo CD reports drift and
waits for you.

**Fix:**

```powershell
argocd app get kubeops
argocd app sync kubeops        # or click Sync in the UI
```

If it won't sync: confirm `source.repoURL` points at your real repo, the chart is
pushed to `main`, and the target namespace/permissions are correct. See
[docs/gitops.md](gitops.md).

## GHCR image pull problems

**Symptom:** `ImagePullBackOff` on `ghcr.io/<owner>/kubeops`.

**Fix:**

- Ensure the image/tag actually exists in GHCR (it isn't published until CI runs).
- If the package is **private**, create a pull secret and reference it:

```powershell
kubectl create secret docker-registry ghcr-creds `
  --docker-server=ghcr.io `
  --docker-username=<github-user> `
  --docker-password=<token-with-read:packages> `
  -n kubeops-dev
```

- Or make the GHCR package **public** for easy local pulls.
