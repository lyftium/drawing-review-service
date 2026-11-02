# CI workflow

CI is **enabled** at [`.github/workflows/ci.yml`](../.github/workflows/ci.yml).

It runs lint, tests, evaluation gates, manifest validation (kind + GPU overlays,
vLLM manifests, and the OpenShift kustomize overlay with
`kubeconform -ignore-missing-schemas`), and an image build with a smoke test.

The copy under `ci/github-actions-ci.yml` is kept in sync for reference.
