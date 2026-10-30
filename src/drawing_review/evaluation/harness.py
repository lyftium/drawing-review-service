"""Evaluation harness.

Two separate questions, two separate scores:

1. **Extraction**: did we find the right regions and read them correctly?
   Detection precision/recall at IoU >= 0.5, OCR character error rate, and
   field-level accuracy of the structured interpretation.
2. **Business correctness**: did the review flag the problems a checker would
   flag, and stay quiet on clean drawings? Scored per drawing against the seeded
   defects in the labels.

A model can score well on (1) and still fail (2), and the other way round. Release
gates are applied to both, from ``gates.yaml``.
"""

from __future__ import annotations

import json
from pathlib import Path

import yaml

from ..config import Settings
from ..lineage import dataset_hash, run_record, write_run
from ..parsing import parse
from ..pipeline import Pipeline
from ..schemas import BBox, RegionKind, Severity
from .metrics import cer, match_boxes, prf

FIELDS = [
    "characteristic",
    "tolerance",
    "datums",
    "nominal",
    "upper",
    "lower",
    "datum_letter",
    "part_number",
    "revision",
    "item",
    "quantity",
]
DEFAULT_GATES = Path(__file__).with_name("gates.yaml")


def evaluate(
    data_dir: Path,
    settings: Settings,
    *,
    runs_dir: Path | None = None,
    gates_path: Path = DEFAULT_GATES,
) -> dict:
    labels = sorted((data_dir / "labels").glob("*.json"))
    images = [data_dir / "images" / json.loads(p.read_text())["file"] for p in labels]
    pipe = Pipeline(settings)

    tp = fp = fn = 0
    cer_sum, cer_n = 0.0, 0
    field_ok = field_n = 0
    b_tp = b_fp = b_fn = 0
    verdict_ok = clean_n = clean_flagged = 0
    per_drawing = []

    for label_path, img_path in zip(labels, images, strict=True):
        label = json.loads(label_path.read_text())
        res = pipe.analyze_bytes(img_path.read_bytes())

        truth = [
            (
                r["id"],
                r["kind"],
                BBox(**dict(zip(["x0", "y0", "x1", "y1"], r["bbox"], strict=True))),
            )
            for r in label["regions"]
        ]
        pred = [(i.region_id, i.kind.value, i.bbox) for i in res.items]
        pairs = match_boxes(pred, truth)
        tp += len(pairs)
        fp += len(pred) - len(pairs)
        fn += len(truth) - len(pairs)

        by_pred = {i.region_id: i for i in res.items}
        by_truth = {r["id"]: r for r in label["regions"]}
        for pid, tid in pairs:
            item, t = by_pred[pid], by_truth[tid]
            cer_sum += cer(item.text, t["text"])
            cer_n += 1
            gold = parse(tid, RegionKind(t["kind"]), t["text"])
            for f in FIELDS:
                g = getattr(gold, f)
                if g in (None, []):
                    continue
                field_n += 1
                field_ok += getattr(item.fields, f) == g

        # business level: set of error rules raised vs seeded defects
        raised = {f.rule_id for i in res.items for f in i.findings if f.severity is Severity.ERROR}
        raised |= {f.rule_id for f in res.document_findings if f.severity is Severity.ERROR}
        expected = {d["rule_id"] for d in label["defects"]}
        b_tp += len(raised & expected)
        b_fp += len(raised - expected)
        b_fn += len(expected - raised)
        verdict_ok += bool(raised) == bool(expected)
        if not expected:
            clean_n += 1
            clean_flagged += bool(raised)
        per_drawing.append(
            {"file": label["file"], "expected": sorted(expected), "raised": sorted(raised)}
        )

    n = len(labels)
    report = {
        "n_drawings": n,
        "extraction": {
            "detection": prf(tp, fp, fn),
            "ocr_cer": round(cer_sum / cer_n, 4) if cer_n else None,
            "field_accuracy": round(field_ok / field_n, 4) if field_n else None,
        },
        "business": {
            "defects": prf(b_tp, b_fp, b_fn),
            "verdict_accuracy": round(verdict_ok / n, 4) if n else None,
            "clean_false_alarm_rate": round(clean_flagged / clean_n, 4) if clean_n else None,
        },
        "per_drawing": per_drawing,
    }
    report["gates"] = apply_gates(report, yaml.safe_load(gates_path.read_text()))
    report["lineage"] = run_record(
        "eval",
        config_hash=settings.fingerprint(),
        backends=pipe.backends.describe(),
        dataset=dataset_hash(labels + images),
        extra={"stub_noise": settings.stub_noise.model_dump()},
    )
    if runs_dir is not None:
        write_run(
            {
                **report["lineage"],
                "results": {k: report[k] for k in ("extraction", "business", "gates")},
            },
            runs_dir,
        )
    return report


def _get(report: dict, dotted: str):
    cur = report
    for part in dotted.split("."):
        cur = cur[part]
    return cur


def apply_gates(report: dict, gates: dict) -> dict:
    checks = []
    for g in gates["gates"]:
        value = _get(report, g["metric"])
        ok = value is not None and (value >= g["min"] if "min" in g else value <= g["max"])
        checks.append({**g, "value": value, "passed": bool(ok)})
    return {"passed": all(c["passed"] for c in checks), "checks": checks}


def render_markdown(report: dict) -> str:
    ex, bu, ln = report["extraction"], report["business"], report["lineage"]
    d, bd = ex["detection"], bu["defects"]
    lines = [
        f"# Evaluation report ({report['n_drawings']} drawings)",
        "",
        f"git `{ln['git_sha']}` · config `{ln['config_hash']}` · dataset `{ln['dataset_hash']}`"
        f" · backends {', '.join(f'{k}={v}' for k, v in ln['backends'].items())}",
        f"stub noise: {ln['stub_noise']}",
        "",
        "## Extraction",
        f"- detection P/R/F1 @IoU0.5: {d['precision']} / {d['recall']} / {d['f1']}"
        f" (tp={d['tp']} fp={d['fp']} fn={d['fn']})",
        f"- OCR character error rate: {ex['ocr_cer']}",
        f"- field accuracy: {ex['field_accuracy']}",
        "",
        "## Business correctness",
        f"- defect P/R/F1: {bd['precision']} / {bd['recall']} / {bd['f1']}"
        f" (tp={bd['tp']} fp={bd['fp']} fn={bd['fn']})",
        f"- drawing verdict accuracy: {bu['verdict_accuracy']}",
        f"- false alarms on clean drawings: {bu['clean_false_alarm_rate']}",
        "",
        "## Gates",
    ]
    for c in report["gates"]["checks"]:
        bound = f">= {c['min']}" if "min" in c else f"<= {c['max']}"
        lines.append(
            f"- {'PASS' if c['passed'] else 'FAIL'} `{c['metric']}` = {c['value']}"
            f" (needs {bound})"
        )
    lines.append("")
    verdict = "PASSED" if report["gates"]["passed"] else "FAILED"
    lines.append(f"**RELEASE GATE {verdict}**")
    return "\n".join(lines) + "\n"
