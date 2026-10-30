"""Data contracts shared by every stage.

These models are the stable interface of the service. Backends can change; these
shapes only change with a version bump, because downstream review tooling and the
golden regression set depend on them.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator


class RegionKind(StrEnum):
    FCF = "fcf"  # feature control frame (GD&T)
    DIMENSION = "dimension"
    DATUM = "datum"
    TITLE_BLOCK = "title_block"
    BOM_ROW = "bom_row"


class Severity(StrEnum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class BBox(BaseModel):
    model_config = ConfigDict(frozen=True)

    x0: float
    y0: float
    x1: float
    y1: float

    @field_validator("x1")
    @classmethod
    def _x_order(cls, v: float, info):  # noqa: ANN001
        if "x0" in info.data and v <= info.data["x0"]:
            raise ValueError("x1 must be greater than x0")
        return v

    @field_validator("y1")
    @classmethod
    def _y_order(cls, v: float, info):  # noqa: ANN001
        if "y0" in info.data and v <= info.data["y0"]:
            raise ValueError("y1 must be greater than y0")
        return v

    def iou(self, other: BBox) -> float:
        ix0, iy0 = max(self.x0, other.x0), max(self.y0, other.y0)
        ix1, iy1 = min(self.x1, other.x1), min(self.y1, other.y1)
        inter = max(0.0, ix1 - ix0) * max(0.0, iy1 - iy0)
        union = self.area + other.area - inter
        return inter / union if union > 0 else 0.0

    @property
    def area(self) -> float:
        return (self.x1 - self.x0) * (self.y1 - self.y0)


class Region(BaseModel):
    id: str
    page: int = 0
    kind: RegionKind
    bbox: BBox
    score: float = Field(ge=0.0, le=1.0)


class OcrSpan(BaseModel):
    region_id: str
    text: str
    confidence: float = Field(ge=0.0, le=1.0)


class Interpretation(BaseModel):
    """Structured fields for one region. Only the fields relevant to the kind are set."""

    region_id: str
    kind: RegionKind
    characteristic: str | None = None  # e.g. POS, FLAT, PERP
    tolerance: float | None = None
    datums: list[str] = Field(default_factory=list)
    nominal: float | None = None
    upper: float | None = None  # signed deviation, e.g. +0.05
    lower: float | None = None  # signed deviation, e.g. -0.05
    datum_letter: str | None = None
    part_number: str | None = None
    revision: str | None = None
    item: int | None = None
    quantity: int | None = None
    parse_ok: bool = True
    source: str = "rules"  # which interpreter produced it


class Finding(BaseModel):
    rule_id: str
    severity: Severity
    message: str
    region_ids: list[str] = Field(default_factory=list)


class ReviewItem(BaseModel):
    region_id: str
    page: int
    kind: RegionKind
    bbox: BBox
    text: str
    fields: Interpretation
    confidence: float
    findings: list[Finding] = Field(default_factory=list)
    # The service never approves anything. A person does.
    status: str = "pending_review"


class Lineage(BaseModel):
    service_version: str
    git_sha: str
    config_hash: str
    backends: dict[str, str]


class AnalysisResult(BaseModel):
    document_id: str  # sha256 of the uploaded bytes; never the file name
    pages: int
    items: list[ReviewItem]
    document_findings: list[Finding]
    summary: dict[str, int]
    timings_ms: dict[str, float]
    lineage: Lineage


class ErrorBody(BaseModel):
    error: str
    detail: str
    request_id: str
