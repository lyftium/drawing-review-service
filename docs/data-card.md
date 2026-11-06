# Data card (evaluation / reference set)

**Status.** Demonstrator data card. Synthetic public set only.
**Linked system.** Drawing-review assist (`drawing-review-service`).

## Dataset identity

| Field | Value |
|---|---|
| Name | Public golden / reference set under `golden/` |
| Purpose | Software gates + extraction metrics before release |
| Sensitivity | Synthetic; no customer IP, no export-controlled drawings |
| Versioning | Content hash recorded as `dataset_hash` in eval run JSON |

## Provenance and rights

- Labels and images authored for this demo (or clearly marked fixtures).
- Not derived from proprietary aerospace programmes in this public tree.
- If a private programme set is used later: keep it offline, document licence / DUA, and never push binaries or OCR text to GitHub.

## Collection and labelling

- Schema: fields expected by the extractors + defect flags for business gates.
- Labelling: deterministic fixtures preferred; any LLM-assisted labels must be human-checked before entering the gate set.
- Split policy: hold out geometries / layouts so the same drawing family does not leak across train/eval when a fine-tune is involved (see LoRA recipe).

## Quality controls

| Control | How |
|---|---|
| Hash integrity | `dataset_hash` over labels + images |
| Gate thresholds | `gates.yaml` — fail closed |
| Separation | Tests / eval metrics / business gates kept distinct (`docs/mlops.md`) |
| Drift | Reviewer disagreements feed new labelled cases |

## Retention and access

- Public fixtures: MIT-licensed repo content.
- Production drawings (if ever): least privilege, no prompt logging of content by default, retention per organisation policy — **not configured in this public demo**.

## Known gaps

- Coverage is narrow (synthetic layouts).
- Does not represent shop-floor scan quality or multi-language title blocks.
- Not a statistical claim about production defect rates.
