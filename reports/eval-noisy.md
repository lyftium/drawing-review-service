# Evaluation report (12 drawings)

git `4770ecc04298` · config `d862bbae80a8` · dataset `c1cb983a34a79644` · backends detector=stub-detector/1, ocr=stub-ocr/1, interpreter=rules-interpreter/1
stub noise: {'drop_rate': 0.05, 'jitter_px': 4.0, 'char_error_rate': 0.03}

## Extraction
- detection P/R/F1 @IoU0.5: 1.0 / 0.9419 / 0.9701 (tp=146 fp=0 fn=9)
- OCR character error rate: 0.0233
- field accuracy: 0.7658

## Business correctness
- defect P/R/F1: 0.6667 / 0.8333 / 0.7407 (tp=10 fp=5 fn=2)
- drawing verdict accuracy: 0.6667
- false alarms on clean drawings: 0.75

## Gates
- PASS `extraction.detection.recall` = 0.9419 (needs >= 0.9)
- PASS `extraction.ocr_cer` = 0.0233 (needs <= 0.05)
- FAIL `business.defects.recall` = 0.8333 (needs >= 0.95)
- FAIL `business.clean_false_alarm_rate` = 0.75 (needs <= 0.1)

**RELEASE GATE FAILED**
