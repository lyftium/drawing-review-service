from __future__ import annotations

from typing import Protocol

from PIL import Image

from ..ingest import Document
from ..preprocess import Page
from ..schemas import Interpretation, OcrSpan, Region


class Detector(Protocol):
    version: str

    def ready(self) -> bool: ...

    def detect(self, doc: Document, page: Page) -> list[Region]: ...


class OcrEngine(Protocol):
    version: str

    def ready(self) -> bool: ...

    def read(self, doc: Document, page: Page, region: Region) -> OcrSpan: ...


class Interpreter(Protocol):
    version: str

    def ready(self) -> bool: ...

    def interpret(self, crop: Image.Image, region: Region, span: OcrSpan) -> Interpretation: ...
