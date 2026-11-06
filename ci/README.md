# CI workflow

The live workflow is [`.github/workflows/ci.yml`](../.github/workflows/ci.yml). It is enabled on `main`.

It runs lint, tests, evaluation gates, manifest validation (Kind + GPU overlays, vLLM manifests, and the OpenShift kustomize overlay with `kubeconform -ignore-missing-schemas`), and an image build with a smoke test. A green run covers that scope. It does not apply the service on a GPU cluster.
