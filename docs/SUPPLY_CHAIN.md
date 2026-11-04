# Supply chain / cold-start inventory

Air-gap honesty: what this demo needs offline, and what is still network-bound.

## Image & runtime

| Item | Pin / note |
|---|---|
| Base image | See `Dockerfile` `FROM` lines (multi-stage) |
| Runtime user | `USER 10001:10001` — non-root; OpenShift random UID friendly |
| Python deps | `requirements.lock` + `requirements-dev.txt` |
| App install | `pip install --no-deps -e .` after lock install |

## Weights (optional backends)

Default stubs need **no** weights. Real backends require local paths / PVC:

| Backend | Env | Offline flag |
|---|---|---|
| YOLO | `DRW_YOLO_WEIGHTS` | pre-place file; do not rely on hub at serve time |
| HF / VLM | `HF_HOME` + revision pins in config | `HF_HUB_OFFLINE=1` fails closed if missing |

## Digests

Record image digests in [`image-digests.md`](image-digests.md) only after a real `docker push`. Until then digests are **null** in [`releases/`](../releases/).

## Cold-start check (laptop)

```bash
# With stubs — no model download required:
make install && make test && make eval
make validate   # kubeconform; needs kustomize + kubeconform binaries
```

Docker build / Kind apply need registry access; when Docker Hub DNS fails, record the failure in `docs/evidence/` rather than inventing digests.

## Related

- Release identity: `releases/schema.json` + filled example
- Risk / air-gap notes: `docs/risk-register.md`
