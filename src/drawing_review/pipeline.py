"""The pipeline: ingestion -> preprocessing -> detection -> OCR -> interpretation
-> consistency checks -> review output.

Pure orchestration. No HTTP, no model code: that lives in ``api`` and ``backends``.
"""

from __future__ import annotations

import time
from contextlib import contextmanager
from functools import lru_cache

from . import __version__
from .backends import Backends, build_backends
from .checks import check_document
from .config import Settings
from .ingest import Document, load_document
from .lineage import git_sha
from .metrics import FINDINGS, REGIONS, STAGE_LATENCY
from .preprocess import preprocess
from .schemas import AnalysisResult, Finding, Lineage, ReviewItem, Severity


class Pipeline:
    def __init__(self, settings: Settings, backends: Backends | None = None):
        self.settings = settings
        self.backends = backends or build_backends(settings)

    def lineage(self) -> Lineage:
        return Lineage(
            service_version=__version__,
            git_sha=_sha(),
            config_hash=self.settings.fingerprint(),
            backends=self.backends.describe(),
        )

    def analyze_bytes(self, data: bytes) -> AnalysisResult:
        timings: dict[str, float] = {}
        with _stage("ingest", timings):
            doc = load_document(data, self.settings)
        return self.analyze(doc, timings)

    def analyze(self, doc: Document, timings: dict[str, float] | None = None) -> AnalysisResult:
        timings = timings if timings is not None else {}
        b = self.backends
        with _stage("preprocess", timings):
            pages = preprocess(doc.pages, self.settings.target_long_side)

        regions, spans, interps, crops = [], {}, {}, {}
        with _stage("detect", timings):
            for page in pages:
                regions.extend((page, r) for r in b.detector.detect(doc, page))
        with _stage("ocr", timings):
            for page, r in regions:
                spans[r.id] = b.ocr.read(doc, page, r)
        with _stage("interpret", timings):
            for page, r in regions:
                bb = r.bbox
                crops[r.id] = page.image.crop((int(bb.x0), int(bb.y0), int(bb.x1), int(bb.y1)))
                interps[r.id] = b.interpreter.interpret(crops[r.id], r, spans[r.id])
        with _stage("checks", timings):
            per_region, doc_findings = check_document(list(interps.values()), self.settings)

        items = []
        for _, r in regions:
            conf = round(min(r.score, spans[r.id].confidence), 3)
            findings = list(per_region[r.id])
            if conf < self.settings.low_confidence:
                findings.append(
                    Finding(
                        rule_id="R010",
                        severity=Severity.WARNING,
                        message="Low confidence: check this region by eye.",
                        region_ids=[r.id],
                    )
                )
            items.append(
                ReviewItem(
                    region_id=r.id,
                    page=r.page,
                    kind=r.kind,
                    bbox=r.bbox,
                    text=spans[r.id].text,
                    fields=interps[r.id],
                    confidence=conf,
                    findings=findings,
                )
            )
            REGIONS.labels(kind=r.kind.value).inc()

        all_findings = [f for i in items for f in i.findings] + doc_findings
        for f in all_findings:
            FINDINGS.labels(rule_id=f.rule_id, severity=f.severity.value).inc()
        summary = {
            "regions": len(items),
            "errors": sum(f.severity is Severity.ERROR for f in all_findings),
            "warnings": sum(f.severity is Severity.WARNING for f in all_findings),
            "pending_review": len(items),
        }
        return AnalysisResult(
            document_id=doc.document_id,
            pages=len(pages),
            items=items,
            document_findings=doc_findings,
            summary=summary,
            timings_ms={k: round(v, 2) for k, v in timings.items()},
            lineage=self.lineage(),
        )


@lru_cache(maxsize=1)
def _sha() -> str:
    return git_sha()


@contextmanager
def _stage(name: str, timings: dict[str, float]):
    t0 = time.perf_counter()
    try:
        yield
    finally:
        dt = time.perf_counter() - t0
        timings[name] = dt * 1000
        STAGE_LATENCY.labels(stage=name).observe(dt)
