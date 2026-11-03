# OpenShift AI model serving notes

How this service sits next to a shared inference stack on OpenShift AI. The model
side is implemented with KServe in `deploy/openshift-ai/`; details and trade-offs in
[`kserve.md`](kserve.md).

## Placement

```
users -> Route / AI Gateway (OIDC, quotas, request-id)
      -> drawing-review Service (business API, no GPU)
      -> KServe InferenceService "llava" (vLLM ServingRuntime, GPU pool)
Training Operator -> PyTorchJob (DDP/FSDP fine-tunes) -> model registry / PVC
```

## Integration steps for a product team

1. Keep business logic in a non-GPU Deployment (this API).
2. Call the platform model route (OpenAI-compatible) instead of baking weights in the app image.
3. Pass request-id and model revision into lineage on every response.
4. Promote models only after eval gates (companion Job) pass on the golden set.
5. Use restricted SCC defaults: no fixed UID, read-only root, drop ALL caps.

## Related files

- deploy/openshift-ai/ + deploy/kserve/ (ServingRuntime, InferenceService, NetworkPolicies)
- docs/kserve.md
- deploy/openshift/ (Route + SCC patch + PyTorchJob)
- deploy/k8s/vllm/vllm-llava.yaml
- docs/gateway.md
- docs/openshift.md
