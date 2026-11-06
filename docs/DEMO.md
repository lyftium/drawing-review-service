# Interview demo — drawing review service

Walkthrough for a screener. Stick to artefacts in this repo.

## 90 seconds

1. **Question:** how do you turn a local prototype into something callable, scored, and cluster-ready?
2. Open the README “Start here” block.
3. Point at CI, [`docs/evidence/kind-apply/`](evidence/kind-apply/), [`docs/image-digests.md`](image-digests.md).
4. **Limits out loud:** CPU stubs by default; GPU OpenShift not applied live.

## 10 minutes

```bash
make install && make test
make eval
make validate
# optional if Kind + image available:
# make deploy-kind && ./scripts/demo_rollback.sh
```

| Minute | Show | Say |
|---|---|---|
| 0–2 | Architecture diagram | Contracts first; backends pluggable |
| 2–4 | `pytest` / golden | Non-regression before changing backends |
| 4–6 | `deploy/` + OpenShift notes | Schema-validated ≠ live GPU; Kind Ready exists |
| 6–8 | `docs/runbook.md` | Pending events first — don’t add GPUs before diagnosis |
| 8–9 | Digest + rollback transcript | Release identity + undo |
| 9–10 | Limits | Shared GPU OpenShift AI apply; measured TTFT still next |

## Do not claim

- Live GPU OpenShift / customer cluster apply
- Invented tok/s or model quality metrics
- That Kind Ready equals production hardening
