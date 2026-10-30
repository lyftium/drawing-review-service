"""CPU-only stand-ins for the detector and OCR.

They read the ground-truth annotations that the synthetic generator embeds in each
PNG (text chunk ``drw:annotations``) and can degrade them with seeded, configurable
noise: dropped regions, jittered boxes, character substitutions. That makes the whole
pipeline, the API and the evaluation harness testable on a laptop with no weights.

These are test doubles. Scores produced with them describe the harness and the
rules engine, not the quality of any model.
"""

from __future__ import annotations

import json
import random
import string

from ..config import StubNoise
from ..ingest import Document
from ..preprocess import Page
from ..schemas import BBox, OcrSpan, Region, RegionKind

ANNOTATION_KEY = "drw:annotations"


def _annotations(doc: Document, page_index: int) -> list[dict]:
    raw = doc.metadata.get(ANNOTATION_KEY)
    if not raw:
        return []
    return [a for a in json.loads(raw) if a.get("page", 0) == page_index]


def _rng(doc: Document, salt: str) -> random.Random:
    return random.Random(f"{doc.document_id}:{salt}")  # noqa: S311 (simulation, not crypto)


class StubDetector:
    version = "stub-detector/1"

    def __init__(self, noise: StubNoise | None = None):
        self.noise = noise or StubNoise()

    def ready(self) -> bool:
        return True

    def detect(self, doc: Document, page: Page) -> list[Region]:
        rng = _rng(doc, f"det:{page.index}")
        regions = []
        for a in _annotations(doc, page.index):
            if rng.random() < self.noise.drop_rate:
                continue
            j = self.noise.jitter_px
            x0, y0, x1, y1 = (v * page.scale for v in a["bbox"])
            dx, dy = rng.uniform(-j, j), rng.uniform(-j, j)
            regions.append(
                Region(
                    id=a["id"],
                    page=page.index,
                    kind=RegionKind(a["kind"]),
                    bbox=BBox(x0=x0 + dx, y0=y0 + dy, x1=x1 + dx, y1=y1 + dy),
                    score=round(rng.uniform(0.75, 0.99), 3),
                )
            )
        return regions


class StubOcr:
    version = "stub-ocr/1"

    def __init__(self, noise: StubNoise | None = None):
        self.noise = noise or StubNoise()

    def ready(self) -> bool:
        return True

    def read(self, doc: Document, page: Page, region: Region) -> OcrSpan:
        truth = {a["id"]: a["text"] for a in _annotations(doc, page.index)}
        text = truth.get(region.id, "")
        rng = _rng(doc, f"ocr:{region.id}")
        chars = list(text)
        errors = 0
        for i, c in enumerate(chars):
            if c.isalnum() and rng.random() < self.noise.char_error_rate:
                chars[i] = rng.choice(string.ascii_uppercase + string.digits)
                errors += 1
        conf = 0.98 - (errors / max(len(text), 1))
        conf = max(0.0, round(conf, 3))
        return OcrSpan(region_id=region.id, text="".join(chars), confidence=conf)
