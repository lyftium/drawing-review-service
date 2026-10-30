"""Stable, comparable view of an analysis result for the golden regression set.

Timings and lineage are excluded on purpose: they change on every run.
"""

from __future__ import annotations

from .schemas import AnalysisResult


def snapshot(res: AnalysisResult) -> dict:
    return {
        "document_id": res.document_id,
        "items": [
            {
                "region_id": i.region_id,
                "kind": i.kind.value,
                "text": i.text,
                "fields": i.fields.model_dump(
                    exclude_defaults=True, exclude={"region_id", "kind", "source"}
                ),
                "findings": sorted(f.rule_id for f in i.findings),
            }
            for i in res.items
        ],
        "document_findings": sorted(f.rule_id for f in res.document_findings),
        "summary": res.summary,
    }
