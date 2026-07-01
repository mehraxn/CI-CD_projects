# GitOps with Argo CD

This explains the GitOps model used by KubeOps and how to drive the Argo CD
`Application` in [argocd/application.yaml](../argocd/application.yaml).

> **Important:** Argo CD is **not installed** by this project. The repo only
> ships the `Application` manifest and this guide. You install Argo CD yourself
> when you're ready.

## What GitOps means

GitOps makes **Git the single source of truth** for what runs in the cluster.
Instead of running `kubectl apply` or `helm install` by hand, you commit the
desired state to Git, and a controller (Argo CD) continuously **reconciles** the
cluster to match Git. Benefits:

- the repo is an auditable history of every change,
- rollbacks are just reverting a commit,
- drift (manual `kubectl edit`) can be detected and optionally reverted.

## How Argo CD watches Git

Argo CD runs inside the cluster and, for each `Application`, polls the configured
Git repo/path/revision. It compares the rendered desired state against what's
live and reports the app as **Synced** or **OutOfSync**. Whether it acts on drift
automatically depends on the sync policy (below).

Our [argocd/application.yaml](../argocd/application.yaml):

- `metadata.namespace: argocd` — the Application object lives where Argo CD runs.
- `source.repoURL: https://github.com/mehraxn/kubeops-gitops.git` — the Git
  repository Argo CD watches (this repo).
- `source.path: helm/kubeops` — the Helm chart to deploy.
- `source.targetRevision: main` — the branch to track.
- `source.helm.valueFiles: [values-dev.yaml]` — values (relative to the path).
- `destination.server: https://kubernetes.default.svc` + `namespace: kubeops-dev`.
- `syncPolicy.syncOptions: [CreateNamespace=true]` — create `kubeops-dev` on
  first sync.
- The `automated:` block is **commented out**, so sync is **manual** by default.

## How to install Argo CD later

```powershell
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
kubectl wait --for=condition=available --timeout=300s deployment/argocd-server -n argocd

# Get the initial admin password:
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d

# Open the UI via port-forward:
kubectl port-forward svc/argocd-server -n argocd 8080:443
# then browse https://localhost:8080  (user: admin)
```

(Optional) install the Argo CD CLI to use `argocd` commands.

## How to apply the Application manifest

1. Edit [argocd/application.yaml](../argocd/application.yaml) and set
   `source.repoURL` to your real repository.
2. Make sure your chart is pushed to that repo on the `main` branch.
3. Apply the manifest:

```powershell
kubectl apply -f argocd/application.yaml
kubectl get applications -n argocd
```

Argo CD now sees the app. With manual sync, it will likely show **OutOfSync**
until you sync.

## How to sync

**From the UI:** open the `kubeops` application and click **Sync**.

**From the CLI:**

```powershell
argocd app get kubeops
argocd app sync kubeops
```

## Manual vs automated sync

**Manual (current default).** Argo CD reports drift but waits for you to click
Sync / run `argocd app sync`. Safest for a portfolio/demo — nothing deploys
unexpectedly.

**Automated.** To let Argo CD apply changes from Git automatically, uncomment the
`automated:` block in the manifest and re-apply:

```yaml
  syncPolicy:
    syncOptions:
      - CreateNamespace=true
    automated:
      prune: true       # delete resources removed from Git
      selfHeal: true    # revert manual changes back to Git state
```

```powershell
kubectl apply -f argocd/application.yaml
```

- `prune: true` deletes cluster resources that were removed from Git.
- `selfHeal: true` reverts any manual `kubectl edit` back to the Git state.

## How to rollback

**GitOps way (preferred):** revert the commit in Git; Argo CD syncs back to the
previous state.

**Argo CD history:**

```powershell
argocd app history kubeops
argocd app rollback kubeops <REVISION>
```

You can also roll back at the Helm layer directly — see
[docs/helm.md](helm.md#rollback) — though with GitOps the Git revert is the
canonical approach.

## Troubleshooting

`OutOfSync` and related issues are covered in
[docs/troubleshooting.md](troubleshooting.md#argo-cd-outofsync).
