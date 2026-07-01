# Security

This lists the security measures that are **actually implemented** in the repo,
followed by an honest list of what is **not** done. This is a local portfolio
project, so the goal is good hygiene and correct defaults, not a hardened
production posture.

## Implemented

### No committed secrets

- The only committed secret file is
  [k8s/secret.example.yaml](../k8s/secret.example.yaml), which contains a clearly
  labelled **placeholder** (`replace-me-with-a-real-secret`).
- The real Secret path `k8s/secret.yaml` is **gitignored** (see
  [.gitignore](../.gitignore)), so real values never land in Git.
- The Helm default `secret.values.APP_SECRET_KEY` in
  [helm/kubeops/values.yaml](../helm/kubeops/values.yaml) is an obvious
  placeholder meant to be overridden per environment;
  [values-prod.yaml](../helm/kubeops/values-prod.yaml) uses
  `secret.create: false` + `existingSecret` so prod secrets are provisioned
  out-of-band.
- App defaults (`APP_SECRET_KEY=dev-insecure-change-me` in
  [app/settings.py](../app/settings.py)) are deliberately obvious so they can't
  be mistaken for a real secret.

### Non-root Docker user

The [Dockerfile](../Dockerfile) creates and switches to an unprivileged user
(uid 1000) before running uvicorn, so the container does not run as root.

### Kubernetes securityContext

The Deployment (raw and Helm) sets:

```yaml
runAsNonRoot: true
runAsUser: 1000
allowPrivilegeEscalation: false
readOnlyRootFilesystem: true
```

`readOnlyRootFilesystem: true` is enabled because the app writes nothing to disk
and `PYTHONDONTWRITEBYTECODE=1` prevents `.pyc` writes — both pods reach
`READY 1/1` with it on.

### Resource limits

Requests/limits are set (`100m`/`128Mi` → `500m`/`256Mi`) to bound resource use
and enable sane scheduling. This also limits the blast radius of a runaway pod.

### Static analysis & scanning

- **bandit** — Python security linter (`bandit -r app`).
- **pip-audit** — dependency vulnerability scan
  (`pip-audit -r requirements.txt`).
- **Trivy** — container image scan. Runs in CI (both
  [`ci.yml`](../.github/workflows/ci.yml) and
  [`image-release.yml`](../.github/workflows/image-release.yml)), failing the
  build on HIGH/CRITICAL vulnerabilities; run locally with
  `trivy image kubeops:local`.

bandit and pip-audit are available locally via the [Makefile](../Makefile)
(`make check`) and run in CI on every push/PR.

### CI secret handling

The GitHub Actions workflows use **GitHub-provided credentials** to push to
**GHCR** (`permissions: packages: write`, `GITHUB_TOKEN`), so no long-lived
registry secret is stored in the repo — see
[README → CI/CD](../README.md#cicd-explanation). The workflows are committed;
they run on GitHub after the first push (and only when this project is the
repository root — see the note in the workflow files).

## Limitations (honest)

- **No authentication / authorization.** Every endpoint is open. There is no
  login, API key, or RBAC on the app itself.
- **In-memory data.** Notes are stored in process memory and **reset on restart**
  — no persistence, no backups.
- **kind is not cloud.** The local kind cluster is for development; it is not a
  managed, hardened, multi-node production cluster.
- **No HTTPS by default.** The Service/Ingress serve plain HTTP. No TLS /
  cert-manager is configured.
- **No External Secrets Operator / secret manager.** Secrets are plain
  Kubernetes Secrets (base64, not encrypted at rest by default in this setup).
- **No NetworkPolicies.** Pod-to-pod traffic is unrestricted within the cluster.
- **No image signing / SBOM / admission policies.** No Cosign, no policy engine
  (e.g. Kyverno/OPA), no kube-score/kube-linter gates yet.
- **CI has not run yet.** The workflows are committed but only execute on GitHub
  after the first push, so no green run exists to point at yet.

## Hardening ideas (future)

See the [README → Future improvements](../README.md#future-improvements): HTTPS
via cert-manager, External Secrets Operator, NetworkPolicies, Cosign signing,
policy checks, and Dependabot.
