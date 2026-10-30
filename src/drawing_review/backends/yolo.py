"""YOLO region detector (ultralytics). Optional extra: ``pip install .[yolo]``.

Not exercised in CI: there are no weights in this repository. The class map must
match the one the model was trained with; it is read from the model itself.
"""

from __future__ import annotations

from ..ingest import Document
from ..preprocess import Page
from ..schemas import BBox, Region, RegionKind


class YoloDetector:
    def __init__(self, weights: str, device: str = "cpu", conf: float = 0.25):
        from ultralytics import YOLO  # lazy: heavy import

        self.model = YOLO(weights)
        self.device = device
        self.conf = conf
        self.version = f"yolo/{weights.rsplit('/', 1)[-1]}"

    def ready(self) -> bool:
        return self.model is not None

    def detect(self, doc: Document, page: Page) -> list[Region]:
        res = self.model.predict(
            page.image.convert("RGB"), device=self.device, conf=self.conf, verbose=False
        )[0]
        names = res.names
        out = []
        for i, (box, cls, score) in enumerate(
            zip(
                res.boxes.xyxy.tolist(),
                res.boxes.cls.tolist(),
                res.boxes.conf.tolist(),
                strict=True,
            )
        ):
            try:
                kind = RegionKind(names[int(cls)])
            except ValueError:
                continue  # class not used by this pipeline
            out.append(
                Region(
                    id=f"p{page.index}-r{i}",
                    page=page.index,
                    kind=kind,
                    bbox=BBox(x0=box[0], y0=box[1], x1=box[2], y1=box[3]),
                    score=float(score),
                )
            )
        return out
