# Demo path (screener / interview)

No company names. Use only what this repository proves.

## 90 seconds

1. Problem: notebook → callable, scored, cluster-prepared component.
2. Show top README table (Verify / Status).
3. Point at evidence: CI badge, [`docs/evidence/kind-apply/`](evidence/kind-apply/), [`docs/image-digests.md`](image-digests.md).
4. State limits: CPU stubs by default; GPU OpenShift not applied live.

## 10 minutes (laptop)

```bash
make install && make test          # 57 CPU tests
make eval                          # golden gates
make validate                      # kubeconform overlays
# optional if Kind + image available:
# make deploy-kind && ./scripts/demo_rollback.sh
```

Talk track while commands run:

| Minute | Show | Say |
|---|---|---|
| 0–2 | Architecture mermaid | Contracts first; backends pluggable |
| 2–4 | `pytest` / golden | Non-regression before changing backends |
| 4–6 | `deploy/k8s` + OpenShift notes | Schema-validated ≠ live GPU; Kind Ready exists |
| 6–8 | `docs/runbook.md` Pending tree | Events first — do not add GPUs before diagnosis |
| 8–9 | Digest + rollback transcript | Release identity + undo procedure |
| 9–10 | Limits + next | Shared GPU OpenShift AI apply; measured TTFT |

## Do not claim

- Live GPU OpenShift / customer cluster apply
- Invented tok/s or quality metrics
- That Kind Ready equals production hardening
