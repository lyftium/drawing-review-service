# CI workflow

The enabled workflow is [`.github/workflows/ci.yml`](../.github/workflows/ci.yml); [`ci/github-actions-ci.yml`](github-actions-ci.yml) is a copy of its source template.

CI runs lint, CPU unit/integration tests, the synthetic evaluation gates, manifest validation, an image build and smoke test, and a GHCR publish on the appropriate branch events. See the workflow for exact triggers and jobs. These checks exercise stubs and packaging; they do not download model weights or run GPU-backed inference.
