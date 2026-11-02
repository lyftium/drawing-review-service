# AI Act–style engineering checklist (not a legal claim)

**Scope.** This maps concrete controls already in this repository to themes that appear in EU AI Act–style governance discussions (traceability, human oversight, quality management, cybersecurity, post-market monitoring). It is an **engineering checklist for interviews and design reviews**. It is **not** a conformity assessment, legal opinion, or claim that the system is AI Act compliant.

High-risk classification, notified bodies, and organisational QMS sit outside what a public demo repo can assert.

## Control map

| Theme (plain language) | What this repo implements | Where |
|---|---|---|
| **Traceability / logging of AI system use** | Every analysis response carries lineage: git sha, backend versions, config hash. Eval runs also record dataset hash and scores. | `lineage.py`, API `lineage` field, `docs/mlops.md` |
| **Data / quality management (evaluation before release)** | Separate software tests, extraction metrics, and business defect gates. Release blocked when `gates.yaml` fails. | `evaluation/`, `gates.yaml`, CI eval step, `deploy/k8s/base/job-eval.yaml` |
| **Human oversight (HITL)** | Pipeline ends in engineer review artefacts (CSV / decisions). Reviewer decisions are the intended feedback loop into the reference set. | `review.py`, runbook / mlops release path |
| **Cybersecurity / least privilege (runtime)** | Restricted Pod Security defaults, dropped capabilities, read-only root FS, NetworkPolicy (only `ai-gateway` may call the API; API may reach vLLM + DNS). | `deploy/k8s/base/`, OpenShift SCC patch |
| **Logging that does not leak sensitive content** | Logs hashes, sizes, timings, request ids — never file names or document content. vLLM example disables request logging. | `api.py`, tests, `docs/gateway.md` |
| **Post-deployment monitoring** | Prometheus histograms (request / stage latency, errors, LLM TTFT) + alert rule sketches. | `metrics.py`, `/metrics`, `deploy/monitoring/` |
| **Change control for models** | Image tagged with git sha; eval Job exit code 1 on gate failure; RollingUpdate with `maxUnavailable: 0` pattern in base Deployment. | Dockerfile `GIT_SHA`, mlops release path |
| **Access control in front of the model** | Design for OIDC, per-team quotas and route ACLs at a gateway (not deployed in this repo). | `docs/gateway.md` |

## What is deliberately not claimed

- Formal risk classification (Annex III / GPAI) or CE marking.
- A full organisational quality management system or notified-body dossier.
- Guarantees about real production drawings (public golden set is synthetic).
- That NetworkPolicy + Prometheus alone satisfy any regulatory article.

## How I would extend this on a real programme

1. Bind lineage fields to the organisation's model card / model registry IDs.
2. Persist reviewer decisions with identity and justification (audit trail).
3. Put gate thresholds and dataset versions under change control with owners.
4. Align gateway auth with the company IdP and retention policy for metrics (not content).
5. Run the same gates on the cluster eval Job against real weights before promotion.

Sibling fine-tuning recipe: run records with git sha / config / data hashes in [lora-finetune-recipe](https://github.com/lyftium/lora-finetune-recipe) — same audit spine for train→eval.
