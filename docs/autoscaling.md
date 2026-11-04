# Autoscaling honesty

GPU serving scale-out has **stages**. This demo does **not** claim measured ready-times.

| Stage | What happens | Measured here? |
|---|---|---|
| Decision | HPA/KEDA fires | **No** — stub only |
| Scheduled | Pod assigned to a node | **No** |
| Image pull | Container layers | **No** (Docker Hub often blocked in this environment) |
| Weights load | Model onto GPU | **No** live apply |
| Ready | Passes readiness probe | Manifests define probes; lag unmeasured |

CPU default HPA is the **wrong** signal for a GPU InferenceService (see `docs/kserve.md`). Prefer queue-depth / KV pressure when you wire KEDA — still mark it unmeasured until timed on a real cluster.

Stub for interview structure only: [`deploy/k8s/base/hpa-stub.yaml`](../deploy/k8s/base/hpa-stub.yaml) — **not** applied, **not** timed.
