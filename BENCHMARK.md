# Drawing-service evaluation benchmark

## What is measured

This benchmark tests the service's evaluation harness with **12 synthetic drawings and deterministic CPU stub backends**. It separates extraction from business-review correctness: detection precision/recall/F1 at IoU 0.5, OCR character error rate, field accuracy, business-defect P/R/F1, drawing-verdict accuracy, and clean-drawing false-alarm rate. It does **not** measure YOLO, Tesseract, VLM, or real-model drawing quality.

No drawing images or source documents are published in this report. The repository generates disposable synthetic images locally.

## Exact commands

```bash
python -m venv .venv && . .venv/bin/activate
make install
drawing-review golden --dir golden

# Clean deterministic stubs
drawing-review eval --data golden --report reports/eval-clean.md

# Noisy deterministic stubs; expected to fail the business release gates
DRW_STUB_CHAR_ERROR_RATE=0.03 DRW_STUB_DROP_RATE=0.05 DRW_STUB_JITTER_PX=4   drawing-review eval --data golden --report reports/eval-noisy.md
```

The `make eval` shortcut generates the images and writes its default clean report to `reports/eval.md`.

Saved measured reports: [`reports/eval-clean.md`](reports/eval-clean.md) and [`reports/eval-noisy.md`](reports/eval-noisy.md).

## Results on the same 12 synthetic drawings

| Metric | Clean stubs | Noisy stubs |
|---|---:|---:|
| Detection precision @ IoU 0.5 | 1.0 | 1.0 |
| Detection recall @ IoU 0.5 | 1.0 | 0.9419 |
| Detection F1 @ IoU 0.5 | 1.0 | 0.9701 |
| Detection TP / FP / FN | 155 / 0 / 0 | 146 / 0 / 9 |
| OCR character error rate | 0.0 | 0.0233 |
| Field accuracy | 1.0 | 0.7658 |
| Business-defect precision / recall / F1 | 1.0 / 1.0 / 1.0 | 0.6667 / 0.8333 / 0.7407 |
| Drawing-verdict accuracy | 1.0 | 0.6667 |
| Clean-drawing false-alarm rate | 0.0 | 0.75 |
| Business release gate | Pass | **Fail** |

The noisy settings are 0.05 drop rate, 4-pixel jitter, and 0.03 character error rate. The individual gate thresholds and outcomes are retained verbatim in the saved reports.

## Interpretation and limits

Acceptable extraction recall can coexist with an unacceptable business result: noisy stubs reduced detection recall to 0.9419 but business-defect recall to 0.8333 and clean-drawing false-alarm rate to 0.75. That is why the service does not equate extracted-symbol quality with drawing-review correctness.

This is a small deterministic stub fixture. It provides repeatability and failure-path evidence, not a real-model accuracy claim, a production quality guarantee, or evidence of GPU-backed deployment. The checked reports include their own config/dataset/backend lineage; their recorded source hash is retained rather than rewritten to look like the current revision.
