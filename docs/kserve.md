# Serving the VLM with KServe

`deploy/kserve/` serves LLaVA through KServe instead of a hand-written vLLM
Deployment; `deploy/openshift-ai/` combines it with the OpenShift overlay.

```bash
kustomize build deploy/openshift-ai | oc apply -f -
oc -n drawing-review get inferenceservice llava   # READY=True once weights are loaded
```

## Why KServe here

The standalone manifest in `deploy/k8s/vllm/` works, but every team that ships a
model would copy it and drift. KServe splits the concern in two:

| Object | Owned by | Contains |
|---|---|---|
| `ServingRuntime` `vllm-openai` | the platform | image, server flags, security context, `/dev/shm`, metrics annotations |
| `InferenceService` `llava` | the model team | model format, weights location, GPU count, model-specific vLLM flags |

A second model on the same runtime is one more short `InferenceService`. On
OpenShift AI the runtime shows up in the dashboard (single-model serving), so
teams can deploy without writing Deployments.

## Decisions

**RawDeployment, not Serverless.** Serverless mode (Knative) brings scale-to-zero
and revision-based canaries, but a 7B VLM takes minutes to load onto GPUs, so a
cold start would land on a user request. RawDeployment gives a plain Deployment,
Service and no service mesh dependency. The cost: no `canaryTrafficPercent`;
model rollouts go through the eval gate and a second `InferenceService` instead.

**One replica, two GPUs.** `--tensor-parallel-size=2` splits each layer across the
two GPUs of the pod (fast interconnect, one copy of the KV cache). Replicas are
pinned to 1: CPU utilisation, the default autoscaling signal, says nothing about a
GPU server. The right signal is vLLM's queue depth (`vllm:num_requests_waiting`)
through KEDA, sized from load-test data (`bench/load_test.py llm`).

**Weights from a PVC, Hub offline.** `storageUri: pvc://model-weights/...` mounts
the volume at `/mnt/models`; `HF_HUB_OFFLINE=1` makes a missing file fail at start
instead of silently downloading. On OpenShift AI the same field takes an S3 data
connection (`s3://...`) instead.

**The API does not change.** The runtime keeps vLLM's OpenAI-compatible server,
so the client in `backends/llava.py` is the same; only the ConfigMap moves:

| Setting | Standalone vLLM | KServe |
|---|---|---|
| `DRW_LLAVA_BASE_URL` | `http://vllm-llava:8000/v1` | `http://llava-predictor/v1` |
| `DRW_LLAVA_MODEL` | `llava-hf/llava-1.5-7b-hf` | `llava` (`--served-model-name={{.Name}}`) |

**Network.** Two extra NetworkPolicies: the API may reach the predictor pods on
8080, and the predictor accepts traffic only from the API and the monitoring
namespaces. Users never get a direct GPU endpoint; they go through the Route (and
the gateway in [`gateway.md`](gateway.md)).

**Restricted security.** The runtime container runs non-root, read-only root
filesystem, no capabilities, RuntimeDefault seccomp; writable paths are explicit
`emptyDir`s (`/tmp`, `/dev/shm`). No fixed UID, so OpenShift `restricted-v2` can
assign one.

## Validation

`make validate` renders `deploy/openshift-ai` and checks every object with
`kubeconform -strict`, using KServe's published CRD schemas from the
[CRDs catalog](https://github.com/datreeio/CRDs-catalog) for `ServingRuntime` and
`InferenceService`. The manifests were also checked in strict mode (unknown
fields rejected) against the CRDs of KServe v0.21.0.

## Not done yet

- Not applied to a live OpenShift AI cluster; no load-time or TTFT numbers from
  this path yet.
- Queue-depth autoscaling (KEDA) is described, not configured.
- KServe's newer `LLMInferenceService` (llm-d: disaggregated prefill/decode,
  KV-cache-aware routing) targets large multi-node LLM serving; for one 7B VLM the
  `InferenceService` path is the simpler fit.
