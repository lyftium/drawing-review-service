"""Tesseract OCR. Optional extra: ``pip install .[ocr]`` plus the tesseract binary."""

from __future__ import annotations

from ..ingest import Document
from ..preprocess import Page
from ..schemas import OcrSpan, Region


class TesseractOcr:
    version = "tesseract/5"

    def __init__(self):
        import pytesseract  # lazy

        self._tess = pytesseract

    def ready(self) -> bool:
        try:
            self._tess.get_tesseract_version()
            return True
        except Exception:
            return False

    def read(self, doc: Document, page: Page, region: Region) -> OcrSpan:
        b = region.bbox
        crop = page.image.crop((int(b.x0), int(b.y0), int(b.x1), int(b.y1)))
        data = self._tess.image_to_data(crop, config="--psm 7", output_type=self._tess.Output.DICT)
        words = [w for w in data["text"] if w.strip()]
        confs = [
            float(c)
            for c, w in zip(data["conf"], data["text"], strict=True)
            if w.strip() and float(c) >= 0
        ]
        conf = (sum(confs) / len(confs) / 100) if confs else 0.0
        return OcrSpan(region_id=region.id, text=" ".join(words), confidence=round(conf, 3))
