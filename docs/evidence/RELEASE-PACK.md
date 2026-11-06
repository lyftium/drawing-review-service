# Release evidence pack

What is **implemented** and **recorded in this repository**, with the boundary of each result.

| Artefact | Path | Evidence | Boundary |
|---|---|---|---|
| CPU tests | [`laptop-smoke-2026-11-04.md`](laptop-smoke-2026-11-04.md) and CI | Service contracts, stubs, and evaluation harness | No GPU or real-model quality |
| Golden evaluation | `make eval` | Synthetic golden-set gates run | Synthetic drawings only |
| Manifest schema | [`kubeconform-2026-11-04.md`](kubeconform-2026-11-04.md) | Kubernetes and optional serving overlays validate | Not a live cluster apply |
| Kind deployment | [`kind-smoke-2026-11-04.md`](kind-smoke-2026-11-04.md) and [`kind-apply/`](kind-apply/) | Local readiness, evaluation completion, and rollback | CPU stubs; local cluster |
| Model/data/risk records | [`../model-card.md`](../model-card.md), [`../data-card.md`](../data-card.md), [`../risk-register.md`](../risk-register.md) | Engineering limits and controls documented | Not a compliance claim |
| CI workflow | [`.github/workflows/ci.yml`](../../.github/workflows/ci.yml) | Enabled lint, test, evaluation, manifest, image, and GHCR jobs | See each run for its commit and status |
| Release identity | [`releases/schema.json`](../../releases/schema.json), [`example-laptop-2026-11-04.json`](../../releases/example-laptop-2026-11-04.json), [`../image-digests.md`](../image-digests.md) | Recorded code/config/image lineage | A digest is not deployment approval |
| Supply chain | [`../SUPPLY_CHAIN.md`](../SUPPLY_CHAIN.md) | Dependency and offline-build notes | Not an air-gapped build proof |

## Local verification

```bash
make install && make test
make eval
make validate   # additionally needs kubectl and kubeconform
```

A further real-model/GPU deployment would need its own weights, environment, evaluation protocol, and evidence. This pack makes no such claim.
