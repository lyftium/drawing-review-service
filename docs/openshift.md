# OpenShift deployment path

This overlay targets OpenShift / OKD (and CRC locally). It is **manifests + docs**, not a claim of production OpenShift AI operations experience. Plain Kubernetes users stay on `deploy/k8s/overlays/*` and Ingress; OpenShift users use the Route and SCC-aware patch here.

## What is in `deploy/openshift/`

| File | Role |
|---|---|
| `kustomization.yaml` | Builds on `../k8s/base`, adds the Route, applies the SCC patch |
| `route.yaml` | OpenShift `Route` with TLS edge termination → Service `drawing-review` |
| `deployment-openshift-patch.yaml` | Restricted security context (non-root, no capabilities, read-only root, seccomp) |
| JSON patches in `kustomization.yaml` | Remove fixed `runAsUser` / `runAsGroup` / `fsGroup` from the Deployment and eval Job so restricted SCC can inject UIDs |
| `networkpolicy-openshift.yaml` | Lets the router (Route traffic) and monitoring namespaces reach port 8080, and allows DNS to `openshift-dns` on 5353 |
| `pytorchjob-ddp.yaml` | Example `PyTorchJob` for the Training Operator (OpenShift AI uses the same CRD family) |

## Why the SCC patch

OpenShift `restricted` / `restricted-v2` assigns an arbitrary UID from the namespace range. A Pod that hard-codes `runAsUser: 10001` (fine on kind) fails admission on OpenShift. The overlay keeps:

- `runAsNonRoot: true`
- `allowPrivilegeEscalation: false`, `capabilities.drop: [ALL]`
- `readOnlyRootFilesystem: true`
- `seccompProfile: RuntimeDefault`

and **removes** the fixed UIDs/GIDs inherited from the base. A strategic-merge patch cannot delete a field by leaving it out, so the removal is done with JSON 6902 `remove` operations; `kustomize build deploy/openshift | grep runAs` should only show `runAsNonRoot`. That matches restricted SCC without requesting privileged or anyuid.

## Local CRC / `oc` path

Prerequisites: [CRC](https://crc.dev/) or a cluster, `oc` logged in, and an image the cluster can pull (build+push, or mirror into the internal registry).

```bash
# Preview rendered YAML
oc kustomize deploy/openshift

# Apply (namespace comes from the kustomization)
oc apply -k deploy/openshift

# Wait and expose
oc -n drawing-review rollout status deploy/drawing-review
oc -n drawing-review get route drawing-review
```

Validate without a cluster (schemas for Route / PyTorchJob may be missing locally):

```bash
kubectl kustomize deploy/openshift | kubeconform -strict -ignore-missing-schemas -summary -
```

`make validate` includes this step.

## OpenShift AI and PyTorchJob

`pytorchjob-ddp.yaml` is a **submit-ready sketch** for the Kubeflow Training Operator CRD (`kubeflow.org/v1` `PyTorchJob`) that OpenShift AI installs. It is not a live Training Operator run from this laptop.

Typical flow on a real OpenShift AI project:

1. Install / enable the Training Operator (or use the OpenShift AI data science project that already has it).
2. Push the training image (`ghcr.io/lyftium/lora-finetune-recipe` or your mirror).
3. Adjust GPU counts, PVC mounts for datasets/outputs, and the config path.
4. `oc apply -f deploy/openshift/pytorchjob-ddp.yaml` and follow Master/Worker pods.

DDP details and the CPU multi-process proof live in the sibling recipe: [lora-finetune-recipe `docs/distributed-training.md`](https://github.com/lyftium/lora-finetune-recipe/blob/main/docs/distributed-training.md).

## Gateway cross-link

Ingress on OpenShift is usually the Route (or a platform gateway in front of it). Auth, quotas, routing and the logging policy (hashes/timings only — never document content) are designed in [`docs/gateway.md`](gateway.md). The base `NetworkPolicy` already expects callers from an `ai-gateway` namespace; wire that namespace to your Envoy / OpenShift gateway of choice rather than exposing the Route to every pod.

## Honest scope

| Claim | Status |
|---|---|
| SCC-aware Deployment overlay + Route | Implemented in-repo |
| `oc apply -k` / CRC instructions | Documented |
| PyTorchJob YAML for Training Operator | Present; not submitted to a live OpenShift AI cluster from this repo |
| Production OpenShift AI serving / metrics tuning | Not claimed — next deepening step |
