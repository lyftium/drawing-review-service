"""Stage 7: human-review output.

The reviewer gets a CSV they can open in a spreadsheet and the full JSON for tools.
Every row starts as ``pending_review``; the service never approves a drawing.
"""

from __future__ import annotations

import csv
import io

from .schemas import AnalysisResult

COLUMNS = [
    "region_id",
    "page",
    "kind",
    "text",
    "confidence",
    "findings",
    "status",
    "reviewer_decision",
    "reviewer_comment",
]


def to_csv(result: AnalysisResult) -> str:
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(COLUMNS)
    for it in result.items:
        w.writerow(
            [
                it.region_id,
                it.page,
                it.kind.value,
                it.text,
                it.confidence,
                "; ".join(f"{f.rule_id}:{f.severity.value}" for f in it.findings),
                it.status,
                "",
                "",
            ]
        )
    for f in result.document_findings:
        w.writerow(
            [
                "(document)",
                "",
                "",
                "",
                "",
                f"{f.rule_id}:{f.severity.value}",
                "pending_review",
                "",
                "",
            ]
        )
    return buf.getvalue()
