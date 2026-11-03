# CI workflow

`ci/github-actions-ci.yml` is the workflow for this repository. It is not enabled
yet: to turn it on, copy it to `.github/workflows/ci.yml` (pushing that path needs
a token with the GitHub `workflow` scope).

It runs lint, tests, evaluation gates, manifest validation (kind + GPU overlays,
vLLM manifests, and the OpenShift kustomize overlay with
`kubeconform -ignore-missing-schemas`), and an image build with a smoke test.
