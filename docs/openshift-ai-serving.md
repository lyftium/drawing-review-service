# OpenShift AI model serving notes

How this service would sit next to a shared inference stack (vLLM / KServe-style) on OpenShift AI.

## Placement

```
users -> Route / AI Gateway (OIDC, quotas, request-id)
      -> drawing-review Service (business API)
      -> vLLM / model-server Service (GPU pool)
Training Operator -> PyTorchJob (DDP/FSDP fine-tunes) -> model registry / PVC
```

## Integration steps for a product team

1. Keep business logic in a non-GPU Deployment (this API).
2. Call the platform model route (OpenAI-compatible) instead of baking weights in the app image.
3. Pass request-id and model revision into lineage on every response.
4. Promote models only after eval gates (companion Job) pass on the golden set.
5. Use restricted SCC defaults: no fixed UID, read-only root, drop ALL caps.

## Related files

- deploy/openshift/ (Route + SCC patch + PyTorchJob)
- deploy/k8s/vllm/vllm-llava.yaml
- docs/gateway.md
- docs/openshift.md
