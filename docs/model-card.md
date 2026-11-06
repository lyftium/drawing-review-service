# Model card (demo drawing-review backends)

**Status.** Engineering model card for this demonstrator. Not a regulatory filing.
**System.** Drawing review assist — extract structured fields from engineering drawings and flag likely defects for human review.
**Owner (demo).** Repository maintainer (`lyftium`).

## Intended use

| Item | Statement |
|---|---|
| Purpose | Assist a human checker; never auto-approve a drawing. |
| Users | Engineers / design-office reviewers in a lab or demo environment. |
| Out of scope | Flight-critical decisions, certification evidence, production release without HITL. |
| Decision affected | Ranking / highlighting of issues for a human; final accept/reject stays with the reviewer. |

## Model / backends in this repo

| Backend | Role | Provenance |
|---|---|---|
| Heuristic / CV extractors | Deterministic baselines for dimensions / title-block style fields | Code in this repository |
| Optional LLM via gateway | Natural-language rationale / OCR-assist when configured | Weights **not** shipped; called through `ai-gateway` / vLLM manifests |
| Golden-set labels | Synthetic reference for gates | `evaluation/` data + hashes |

Pin revisions in deploy config and record them in every `lineage` payload (`git_sha`, backend `version`, `config_hash`).

## Training data (when a fine-tune is used)

- Prefer the sibling recipe [lora-finetune-recipe](https://github.com/lyftium/lora-finetune-recipe) for adapters.
- Do not train on customer drawings in this public repo.
- Record dataset hash, licence, and split policy in the run JSON before promotion.

## Evaluation

- Software tests (`pytest`) ≠ model quality ≠ business gates (`gates.yaml`).
- Eval Job / CI records dataset hash + scores; release blocked on gate failure.
- Public scores are on a **synthetic** golden set — not a claim about production drawings.

## Limitations and failure modes

- OCR / extraction errors on poor scans, unusual title-block layouts, non-Latin scripts.
- LLM path can hallucinate rationales; treat tool/LLM output as untrusted data.
- Latency and quality depend on the serving stack (vLLM concurrency, quantisation); measure before SLO commitments.
- Manifests for KServe / OpenShift AI are **validated offline** unless a live apply note says otherwise.

## Human oversight

Pipeline ends in reviewer artefacts (`reviewer_decision`). Disagreement becomes a labelled case, not only a ticket. See `docs/mlops.md`.

## Security and logging

- Logs: hashes, sizes, timings, request ids — not drawing content or file names.
- Runtime: dropped capabilities, read-only root FS, NetworkPolicy sketches in `deploy/k8s/`.
- Secrets stay out of images.

## Environmental / compute note

Inference cost and GPU memory are measured separately in [vllm-serving-benchmark-t4](https://github.com/lyftium/vllm-serving-benchmark-t4); this card makes no hardware SLO claims.

## Change control

Image tagged with git SHA; RollingUpdate with `maxUnavailable: 0` pattern; rollback via previous image / PVC weights. Formal AI Act classification is organisational — see `docs/ai-act-mapping.md` and `docs/risk-register.md`.
