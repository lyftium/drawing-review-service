"""Multimodal interpreter that calls a LLaVA model served by vLLM.

vLLM exposes an OpenAI-compatible API, so this client only needs ``httpx``. The
model is asked for JSON matching ``Interpretation``; the answer is validated with
pydantic and cross-checked with the deterministic parser. Anything that fails
validation falls back to the parser and is counted, because a VLM that silently
invents a tolerance is worse than one that says nothing.

Only the region crop and its OCR text are sent, never the whole drawing.
"""

from __future__ import annotations

import base64
import io
import json
import time

import httpx
from PIL import Image
from pydantic import ValidationError

from ..metrics import INTERPRETER_FALLBACKS, TTFT
from ..parsing import parse
from ..schemas import Interpretation, OcrSpan, Region

PROMPT = (
    "You read one annotation cropped from an engineering drawing. Kind: {kind}. "
    "OCR text: '{text}'. Return only a JSON object with the keys that apply among: "
    "characteristic, tolerance, datums, nominal, upper, lower, datum_letter, part_number, "
    "revision, item, quantity. Use null when a value is not visible. Do not guess."
)


class LlavaInterpreter:
    def __init__(self, base_url: str, model: str, timeout_s: float = 30.0):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.client = httpx.Client(timeout=timeout_s)
        self.version = f"llava/{model}"

    def ready(self) -> bool:
        try:
            return self.client.get(f"{self.base_url}/models").status_code == 200
        except httpx.HTTPError:
            return False

    def interpret(self, crop: Image.Image, region: Region, span: OcrSpan) -> Interpretation:
        fallback = parse(region.id, region.kind, span.text)
        try:
            raw = self._ask(crop, region, span)
            fields = json.loads(raw)
            vlm = Interpretation(
                region_id=region.id,
                kind=region.kind,
                source="llava",
                **{k: v for k, v in fields.items() if k in Interpretation.model_fields},
            )
        except (httpx.HTTPError, json.JSONDecodeError, ValidationError, TypeError):
            INTERPRETER_FALLBACKS.inc()
            return fallback
        # If OCR parsed cleanly and the VLM disagrees on a numeric value, trust neither
        # silently: keep the parser value and let the review UI show low confidence.
        if fallback.parse_ok and fallback.tolerance != vlm.tolerance and vlm.tolerance is not None:
            INTERPRETER_FALLBACKS.inc()
            return fallback
        return vlm

    def _ask(self, crop: Image.Image, region: Region, span: OcrSpan) -> str:
        buf = io.BytesIO()
        crop.convert("RGB").save(buf, format="PNG")
        b64 = base64.b64encode(buf.getvalue()).decode()
        body = {
            "model": self.model,
            "stream": True,
            "temperature": 0,
            "max_tokens": 200,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}},
                        {
                            "type": "text",
                            "text": PROMPT.format(kind=region.kind.value, text=span.text),
                        },
                    ],
                }
            ],
        }
        start, first, chunks = time.perf_counter(), None, []
        with self.client.stream("POST", f"{self.base_url}/chat/completions", json=body) as r:
            r.raise_for_status()
            for line in r.iter_lines():
                if not line.startswith("data: ") or line == "data: [DONE]":
                    continue
                delta = json.loads(line[6:])["choices"][0]["delta"].get("content") or ""
                if delta and first is None:
                    first = time.perf_counter()
                    TTFT.observe(first - start)
                chunks.append(delta)
        text = "".join(chunks).strip()
        return text[text.find("{") : text.rfind("}") + 1]
