# Drawing review service

![CI](https://github.com/lyftium/drawing-review-service/actions/workflows/ci.yml/badge.svg)

A drawing-analysis workflow is hard to hand over when its models, inputs, and checks live in one local script. This project separates that workflow into a FastAPI service with pluggable inference backends, typed results, a reproducible evaluation harness, and container/Kubernetes packaging. It uses synthetic drawings and keeps every result `pending_review`.

CPU stubs stand in for detection, OCR, and the vision-language model. An engineer can run the API and tests without downloading weights, then use the same interfaces with optional model clients. Full walkthrough: [`docs/DEMO.md`](docs/DEMO.md).

## Example

Uploading the generated `syn-001.png` returns one page, 14 extracted regions, and two errors. Excerpt from the actual stub response:

```json
{
  "pages": 1,
  "summary": {"regions": 14, "errors": 2, "warnings": 0, "pending_review": 14},
  "items": [{
    "region_id": "fcf-3",
    "kind": "fcf",
    "text": "PERP|0.05|C",
    "fields": {"characteristic": "PERP", "tolerance": 0.05, "datums": ["C"]},
    "status": "pending_review"
  }]
}
```

The full response also includes a byte-derived document id, findings, timings, and backend/config lineage. [Reproduce this request](docs/DEMO.md#requestresponse-example).

## Prerequisites and quickstart

Python 3.11+ and `make`; a normal CPU environment is sufficient. Docker, `kubectl`, Kind, and `kubeconform` are only needed for the optional packaging checks.

```bash
python -m venv .venv && . .venv/bin/activate
make install
make test
make eval
```

Expected: tests pass, 12 deterministic golden images are generated under `golden/images/`, and the evaluation report is written to `reports/eval.md`. `make test` does not need the generated images; `make eval` creates them before running the harness.

To serve the API locally:

```bash
uvicorn --factory drawing_review.api:app_factory --port 8080
curl -F file=@golden/images/syn-001.png localhost:8080/v1/analyze
```

## What I implemented

- **API boundary:** multipart input validation, stable Pydantic response/error schemas, JSON and CSV results, liveness/readiness, metrics, and no document content in logs.
- **Backend boundary:** detector, OCR, and interpreter protocols; deterministic stubs plus YOLO, Tesseract, and LLaVA-through-vLLM clients.
- **Evaluation:** synthetic fixtures with known labels, extraction metrics, business-defect gates, and code/backend/config lineage.
- **Packaging:** a non-root container, kustomize overlays, CI tests and manifest checks, and a recorded local Kind deployment with an evaluation job and rollback.

Architecture details: [`docs/architecture.md`](docs/architecture.md). Model and data boundaries: [`docs/model-card.md`](docs/model-card.md) and [`docs/data-card.md`](docs/data-card.md).

## Evaluation and recorded results

Recognizing a symbol is not the same as judging a drawing. I therefore separate **extraction metrics** (detection precision/recall at IoU 0.5, OCR character error rate, field accuracy) from **business gates** (missed defects and false alarms).

Running the documented noisy-stub settings on the 12-drawing synthetic set gives:

| | clean stubs | noisy stubs |
|---|---:|---:|
| detection recall | 1.00 | 0.94 |
| OCR character error rate | 0.000 | 0.023 |
| defect recall (business) | 1.00 | 0.83 |
| false alarms on clean drawings | 0.00 | 0.75 |
| release gate | pass | **fail** |

```bash
drawing-review eval --data golden
DRW_STUB_CHAR_ERROR_RATE=0.03 DRW_STUB_DROP_RATE=0.05 DRW_STUB_JITTER_PX=4 \
  drawing-review eval --data golden
```

These figures test the harness, not YOLO/OCR/LLaVA quality. A misread datum can produce a false alarm while detection still looks acceptable.

## Design decisions

1. **Contracts before models.** Typed inputs, outputs, and backend protocols let CI test the service with CPU stubs instead of silently depending on unavailable weights.
2. **Quality gates include the review decision.** A backend can extract regions but still fail the business gate, so the service exposes both levels of evaluation.
3. **Integration checks leave evidence.** Local Kind deployment, evaluation completion, and rollback transcripts live in [`docs/evidence/kind-apply/`](docs/evidence/kind-apply/); CI and image digests have separate records.

## Container and local Kubernetes checks

```bash
make image
docker run --rm -p 8080:8080 --read-only --tmpfs /tmp drawing-review:dev
make kind-up && make deploy-kind
make validate
```

`make validate` only renders and validates manifests. Actual Kind outcomes and their limits are indexed in [`docs/evidence/README.md`](docs/evidence/README.md).

## Limitations

The public evaluation has 12 synthetic drawings and stub backends. The optional real-model clients and GPU serving manifests are not exercised by CI, and no GPU-backed deployment or model-quality claim is recorded. Kind smoke tests show local integration, not production readiness. The gateway and external authentication shown in the architecture are proposed boundaries, not part of this API.

## Documentation

[Quickstart and walkthrough](docs/DEMO.md) · [Evaluation/MLOps](docs/mlops.md) · [Rollback](docs/rollback.md) · [Observability](docs/observability.md) · [Release controls](checklists/release-approval.md)

[MIT license](LICENSE) — synthetic fixtures generated in this repository; upstream models remain subject to their own licenses.
