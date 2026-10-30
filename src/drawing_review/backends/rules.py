from __future__ import annotations

from PIL import Image

from ..parsing import parse
from ..schemas import Interpretation, OcrSpan, Region


class RulesInterpreter:
    """Deterministic interpretation from OCR text. No model, no GPU."""

    version = "rules-interpreter/1"

    def ready(self) -> bool:
        return True

    def interpret(self, crop: Image.Image, region: Region, span: OcrSpan) -> Interpretation:
        return parse(region.id, region.kind, span.text)
