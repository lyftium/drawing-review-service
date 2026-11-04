# Manifest validation — 2026-11-04 (America/Los_Angeles)

Laptop run of `make validate` (kustomize + kubeconform). **Schema validation only** — not a live cluster apply.

| Target | Result |
|---|---|
| `deploy/k8s/overlays/kind` | 9 resources — Valid: 9, Invalid: 0 |
| `deploy/k8s/overlays/gpu` | 9 resources — Valid: 9, Invalid: 0 |
| `deploy/k8s/vllm/` | 2 resources — Valid: 2, Invalid: 0 |
| `deploy/openshift` | 11 resources — Valid: 10, Skipped: 1 (missing schema), Invalid: 0 |
| `deploy/openshift-ai` | 15 resources — Valid: 14, Skipped: 1 (missing schema), Invalid: 0 |

```text
kubectl kustomize deploy/k8s/overlays/kind | kubeconform -strict -summary -
Summary: 9 resources found parsing stdin - Valid: 9, Invalid: 0, Errors: 0, Skipped: 0
kubectl kustomize deploy/k8s/overlays/gpu | kubeconform -strict -summary -
Summary: 9 resources found parsing stdin - Valid: 9, Invalid: 0, Errors: 0, Skipped: 0
kubeconform -strict -summary deploy/k8s/vllm/
Summary: 2 resources found in 1 file - Valid: 2, Invalid: 0, Errors: 0, Skipped: 0
kubectl kustomize deploy/openshift | kubeconform -strict -ignore-missing-schemas -summary -
Summary: 11 resources found parsing stdin - Valid: 10, Invalid: 0, Errors: 0, Skipped: 1
kubectl kustomize deploy/openshift-ai | kubeconform -strict -ignore-missing-schemas -schema-location default -schema-location 'https://raw.githubusercontent.com/datreeio/CRDs-catalog/main/{{.Group}}/{{.ResourceKind}}_{{.ResourceAPIVersion}}.json' -summary -
Summary: 15 resources found parsing stdin - Valid: 14, Invalid: 0, Errors: 0, Skipped: 1
```

Tooling: `kubeconform` 0.8.0, `kustomize` via Homebrew, macOS arm64.
Full command log: produced by `make validate` on this machine the same day as `docs/evidence/laptop-smoke-2026-11-04.md`.
