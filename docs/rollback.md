# Rollback procedure (drawing-review)

**Status.** Procedure + script for a kind / cluster demo. A captured undo transcript is committed under `docs/evidence/` **only when** a live apply has been run; until then this document is the contract, not a claim that undo was executed here.

## What we roll back

| Layer | Forward | Rollback |
|---|---|---|
| Application image | Deploy image tagged with git SHA | Previous ReplicaSet via `kubectl rollout undo`, or pin prior digest |
| Weights / config | ConfigMap + PVC / env | Restore previous ConfigMap revision or PVC contents; re-run eval gates |
| Evaluation gate | `gates.yaml` thresholds | Fail-closed: do not reopen traffic if gates fail after undo |

Deployment keeps `revisionHistoryLimit: 5` and `maxUnavailable: 0` so undo has history and traffic stays on ready pods.

## Demo script

```bash
# Prerequisites: kubectl context pointing at a namespace where the service was applied
# (e.g. after `make deploy-kind`).
./scripts/demo_rollback.sh
```

The script:

1. Records current image / ReplicaSet
2. Runs `kubectl rollout undo deploy/drawing-review -n drawing-review`
3. Waits for rollout status
4. Prints before/after image refs
5. Reminds you to re-run eval / smoke before reopening any route

## Honesty

- Schema-valid manifests ≠ a completed undo on a live cluster.
- Do not invent digests or timings; paste real `kubectl` output into `docs/evidence/kind-apply/` when you have it.
- Rollback of **model quality** still requires the eval Job + `gates.yaml`, not only a Deployment undo.

Related: `docs/mlops.md`, `docs/risk-register.md`, `docs/runbook.md`.
