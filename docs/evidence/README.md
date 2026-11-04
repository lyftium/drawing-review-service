# Evidence

## Already recorded

| File | What it proves |
|---|---|
| [`laptop-smoke-2026-11-04.md`](laptop-smoke-2026-11-04.md) | 57 pytest (DRS) + 48 pytest (AGS) on laptop; Docker/Kind blocked by registry DNS |
| [`kubeconform-2026-11-04.md`](kubeconform-2026-11-04.md) | `make validate` — kind/gpu/vLLM/OpenShift/OpenShift AI overlays schema-valid (not live-applied) |

## After a live apply (not yet)

Place transcripts here after a successful apply (kind or shared cluster):

- `kind-apply/deploy-*.txt` — kubectl apply / rollout status / get pods
- `kind-apply/rollback-*.txt` — output of `./scripts/demo_rollback.sh`

Do not invent digests, timings, or GPU metrics. Until apply files appear, READMEs correctly say manifests are prepared, not live-applied.
