# Demo — drawing review service

Run the public demonstrator locally with deterministic CPU stubs. The generated images and all annotations are synthetic.

## Prerequisites

- Python 3.11+, `make`
- Optional: Docker, `kubectl`, Kind, and `kubeconform` for packaging checks
- Tests and evaluation use a CPU and download no model weights

## Quickstart

```bash
python -m venv .venv && . .venv/bin/activate
make install
make test
make eval
```

Expected: unit/integration tests pass; `make eval` generates the 12 golden images and writes `reports/eval.md`. Generated images are not committed. To regenerate labels and expected output deliberately, inspect [`scripts/update_golden.py`](../scripts/update_golden.py) first and run `make golden`.

## Request/response example

After `make eval`, start the service and upload one generated image:

```bash
uvicorn --factory drawing_review.api:app_factory --port 8080
# In another shell:
curl -s -F file=@golden/images/syn-001.png localhost:8080/v1/analyze
```

The stub response for this input includes:

```json
{
  "pages": 1,
  "summary": {"regions": 14, "errors": 2, "warnings": 0, "pending_review": 14},
  "items": [{
    "region_id": "fcf-3",
    "kind": "fcf",
    "text": "PERP|0.05|C",
    "fields": {
      "characteristic": "PERP", "tolerance": 0.05, "datums": ["C"],
      "parse_ok": true, "source": "rules"
    },
    "status": "pending_review"
  }],
  "document_findings": [{
    "rule_id": "R008",
    "severity": "error",
    "message": "Duplicate BOM item number. Item 1 appears 2 times.",
    "region_ids": ["bom_row-10", "bom_row-12"]
  }]
}
```

This is an excerpt: the complete response includes the remaining regions, timings, a document hash, and lineage. Replace the image but keep the filename extension; magic bytes, not the filename, determine input validity.

## Packaging and manifest checks

```bash
make image
make validate
```

`make validate` requires `kubectl` and `kubeconform`; it performs no cluster apply. For an actual local smoke test with Docker and Kind:

```bash
make kind-up
make deploy-kind
./scripts/demo_rollback.sh
```

Expected: the deployment becomes Ready, the evaluation Job completes, and rollback ends with healthy/readiness checks OK. Evidence from a prior local run: [`kind-apply/`](evidence/kind-apply/). Image digest notes: [`image-digests.md`](image-digests.md).

## Limitations

- The default path uses CPU stubs and 12 synthetic drawings; it does not measure real detector, OCR, or VLM quality.
- Optional real-model backends and GPU serving manifests have no recorded end-to-end GPU deployment.
- Kind readiness and rollback checks are local integration evidence, not production hardening.
