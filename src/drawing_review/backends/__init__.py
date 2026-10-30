"""Pluggable model backends.

Each stage depends on a small protocol, not on a framework. ``build_backends`` picks
implementations from settings, so swapping the stub detector for YOLO is a config
change, not a code change. Heavy imports (torch, ultralytics, tesseract) happen
lazily inside the real backends, so the API image and the test suite stay small.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..config import Settings
from .base import Detector, Interpreter, OcrEngine


@dataclass
class Backends:
    detector: Detector
    ocr: OcrEngine
    interpreter: Interpreter

    def describe(self) -> dict[str, str]:
        return {
            "detector": self.detector.version,
            "ocr": self.ocr.version,
            "interpreter": self.interpreter.version,
        }

    def ready(self) -> bool:
        return all(b.ready() for b in (self.detector, self.ocr, self.interpreter))


def build_backends(settings: Settings) -> Backends:
    if settings.detector == "yolo":
        from .yolo import YoloDetector

        detector: Detector = YoloDetector(settings.yolo_weights, settings.yolo_device)
    else:
        from .stub import StubDetector

        detector = StubDetector(settings.stub_noise)

    if settings.ocr == "tesseract":
        from .tesseract import TesseractOcr

        ocr: OcrEngine = TesseractOcr()
    else:
        from .stub import StubOcr

        ocr = StubOcr(settings.stub_noise)

    if settings.interpreter == "llava":
        from .llava import LlavaInterpreter

        interpreter: Interpreter = LlavaInterpreter(
            settings.llava_base_url, settings.llava_model, settings.llava_timeout_s
        )
    else:
        from .rules import RulesInterpreter

        interpreter = RulesInterpreter()
    return Backends(detector, ocr, interpreter)
