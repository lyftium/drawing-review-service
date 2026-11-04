# Release evidence pack (drawing-review-service)

Screener checklist: what is **proven in-repo** vs still waiting on environment access.

| Artefact | Path | Proves | Not a claim of |
|---|---|---|---|
| CPU tests | `pytest` / laptop smoke | Service contracts, stubs, eval harness load | GPU / live model quality |
| Golden eval | `make eval` | Gates run on synthetic golden set | Customer drawings |
| Manifest schema | [`kubeconform-2026-11-04.md`](kubeconform-2026-11-04.md) | kind/gpu/vLLM/OpenShift AI overlays validate | Live cluster apply |
| Laptop smoke | [`laptop-smoke-2026-11-04.md`](laptop-smoke-2026-11-04.md) | 57 pytest locally | Docker Hub / Kind (DNS blocked that day) |
| Rollback contract | [`../rollback.md`](../rollback.md) + `scripts/demo_rollback.sh` | Undo procedure exists | Captured undo transcript (needs apply) |
| Governance | `docs/model-card.md`, `data-card.md`, `risk-register.md`, `ai-act-mapping.md` | Engineering artefacts present | Legal conformity |
| CI workflow | `ci/github-actions-ci.yml` | Ready to enable | Green Actions badge (needs `workflow` scope) |

## 90-second verify

```bash
make install && make test
make eval
make validate   # kubeconform — see kubeconform-2026-11-04.md
```

## Still blocked on environment / user token

1. `gh auth refresh -s workflow` → `bash scripts/install-github-actions.sh` + push `.github/workflows/`
2. Docker Hub / Kind DNS → `make deploy-kind` + paste undo under `kind-apply/`
3. Shared GPU OpenShift AI project → apply `deploy/openshift-ai`, measure TTFT, fill `docs/image-digests.md`
