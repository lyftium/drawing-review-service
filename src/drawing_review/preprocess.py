"""Stage 2: preprocessing.

Normalises every page to grayscale and a bounded size so model latency and memory
are predictable. The scale factor is returned so boxes can be mapped back.
"""

from __future__ import annotations

from dataclasses import dataclass

from PIL import Image, ImageOps


@dataclass
class Page:
    index: int
    image: Image.Image
    scale: float  # processed = original * scale


def preprocess(pages: list[Image.Image], target_long_side: int) -> list[Page]:
    out = []
    for i, img in enumerate(pages):
        gray = ImageOps.grayscale(img)
        long_side = max(gray.size)
        scale = 1.0
        if long_side > target_long_side:
            scale = target_long_side / long_side
            gray = gray.resize(
                (round(gray.width * scale), round(gray.height * scale)), Image.Resampling.LANCZOS
            )
        gray = ImageOps.autocontrast(gray)
        out.append(Page(index=i, image=gray, scale=scale))
    return out
