#!/usr/bin/env bash
# Demonstrate Deployment rollback for drawing-review.
# Requires: kubectl, a live apply (e.g. make deploy-kind). Does not invent evidence.
set -euo pipefail

NS="${DRW_NAMESPACE:-drawing-review}"
DEPLOY="${DRW_DEPLOYMENT:-drawing-review}"
TIMEOUT="${DRW_ROLLOUT_TIMEOUT:-120s}"

need() { command -v "$1" >/dev/null || { echo "missing: $1" >&2; exit 1; }; }
need kubectl

if ! kubectl get "deploy/${DEPLOY}" -n "${NS}" >/dev/null 2>&1; then
  cat >&2 <<EOF
Deployment ${DEPLOY} not found in namespace ${NS}.
Apply first (example): make deploy-kind
This script will not fabricate a rollback transcript.
EOF
  exit 2
fi

echo "== before =="
kubectl get "deploy/${DEPLOY}" -n "${NS}" -o wide
BEFORE_IMAGE="$(kubectl get "deploy/${DEPLOY}" -n "${NS}" -o jsonpath='{.spec.template.spec.containers[0].image}')"
echo "image: ${BEFORE_IMAGE}"
kubectl rollout history "deploy/${DEPLOY}" -n "${NS}" | tail -n +1

echo "== undo =="
kubectl rollout undo "deploy/${DEPLOY}" -n "${NS}"
kubectl rollout status "deploy/${DEPLOY}" -n "${NS}" --timeout="${TIMEOUT}"

echo "== after =="
AFTER_IMAGE="$(kubectl get "deploy/${DEPLOY}" -n "${NS}" -o jsonpath='{.spec.template.spec.containers[0].image}')"
kubectl get "deploy/${DEPLOY}" -n "${NS}" -o wide
echo "image: ${AFTER_IMAGE}"

if [[ "${BEFORE_IMAGE}" == "${AFTER_IMAGE}" ]]; then
  echo "NOTE: image unchanged — only one revision may exist, or undo targeted the same image." >&2
fi

cat <<EOF

Next (do not skip):
  1. Smoke: curl the Service /healthz and /readyz
  2. Re-run eval / gates before reopening any Route
  3. Optionally save this terminal output under docs/evidence/kind-apply/rollback-\$(date -u +%Y%m%dT%H%M%SZ).txt
EOF
