# Evaluation report (12 drawings)

git `4770ecc04298` · config `9fcfa453905c` · dataset `c1cb983a34a79644` · backends detector=stub-detector/1, ocr=stub-ocr/1, interpreter=rules-interpreter/1
stub noise: {'drop_rate': 0.0, 'jitter_px': 0.0, 'char_error_rate': 0.0}

## Extraction
- detection P/R/F1 @IoU0.5: 1.0 / 1.0 / 1.0 (tp=155 fp=0 fn=0)
- OCR character error rate: 0.0
- field accuracy: 1.0

## Business correctness
- defect P/R/F1: 1.0 / 1.0 / 1.0 (tp=12 fp=0 fn=0)
- drawing verdict accuracy: 1.0
- false alarms on clean drawings: 0.0

## Gates
- PASS `extraction.detection.recall` = 1.0 (needs >= 0.9)
- PASS `extraction.ocr_cer` = 0.0 (needs <= 0.05)
- PASS `business.defects.recall` = 1.0 (needs >= 0.95)
- PASS `business.clean_false_alarm_rate` = 0.0 (needs <= 0.1)

**RELEASE GATE PASSED**
