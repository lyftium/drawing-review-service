"""Runtime configuration.

Everything that changes between environments comes from environment variables
(prefix ``DRW_``) so the same image runs on a laptop, in kind and on a GPU node.
"""

from __future__ import annotations

import hashlib
import json
import os
from typing import Literal

from pydantic import BaseModel, Field


class StubNoise(BaseModel):
    """Simulated errors for the stub backends, so the evaluation harness has something to catch."""

    drop_rate: float = Field(0.0, ge=0.0, le=1.0)
    jitter_px: float = Field(0.0, ge=0.0)
    char_error_rate: float = Field(0.0, ge=0.0, le=1.0)


class Settings(BaseModel):
    detector: Literal["stub", "yolo"] = "stub"
    ocr: Literal["stub", "tesseract"] = "stub"
    interpreter: Literal["rules", "llava"] = "rules"

    yolo_weights: str = "/models/yolo/best.pt"
    yolo_device: str = "cpu"
    llava_base_url: str = "http://vllm:8000/v1"
    llava_model: str = "llava-hf/llava-1.5-7b-hf"
    llava_timeout_s: float = 30.0

    max_upload_mb: float = Field(20.0, gt=0)
    max_pages: int = Field(20, gt=0)
    max_pixels: int = Field(40_000_000, gt=0)
    target_long_side: int = Field(2000, gt=0)

    max_tolerance_mm: float = Field(5.0, gt=0)
    low_confidence: float = Field(0.5, ge=0, le=1)

    stub_noise: StubNoise = Field(default_factory=StubNoise)

    def fingerprint(self) -> str:
        blob = json.dumps(self.model_dump(), sort_keys=True).encode()
        return hashlib.sha256(blob).hexdigest()[:12]

    @classmethod
    def from_env(cls, env: dict[str, str] | None = None) -> Settings:
        env = dict(os.environ if env is None else env)
        data: dict[str, object] = {}
        for name in cls.model_fields:
            key = f"DRW_{name.upper()}"
            if key in env and name != "stub_noise":
                data[name] = env[key]
        noise = {
            k: env[f"DRW_STUB_{k.upper()}"]
            for k in StubNoise.model_fields
            if f"DRW_STUB_{k.upper()}" in env
        }
        if noise:
            data["stub_noise"] = noise
        return cls.model_validate(data)
