"""Deterministic parser from OCR text to structured fields.

Used directly by the ``rules`` interpreter and as the validation/fallback path for
the multimodal interpreter: if the VLM returns something that does not parse into
the schema, we fall back here rather than guess.

Text conventions (ASCII, as produced by the synthetic generator and by most OCR
engines on GD&T frames):

    fcf        POS|0.10|A|B        FLAT|0.05
    dimension  12.00 +0.05/-0.05   DIA 8.00 +0.02/-0.02
    datum      DATUM A
    title      PN: DRW-0007 REV: B
    bom        1 | BRKT-001 | QTY 2
"""

from __future__ import annotations

import re

from .schemas import Interpretation, RegionKind

CHARACTERISTICS = {
    "POS",
    "FLAT",
    "STRAIGHT",
    "CIRC",
    "CYL",
    "PERP",
    "PARA",
    "ANG",
    "PROF",
    "RUNOUT",
    "CONC",
}
FORM = {"FLAT", "STRAIGHT", "CIRC", "CYL"}
NEEDS_DATUM = {"POS", "PERP", "PARA", "ANG", "RUNOUT", "CONC"}

_NUM = r"[-+]?\d+(?:\.\d+)?"
_DIM = re.compile(rf"^(?:DIA\s+)?(?P<nom>{_NUM})\s+(?P<up>{_NUM})\s*/\s*(?P<lo>{_NUM})$")
_DATUM = re.compile(r"^DATUM\s+(?P<l>[A-Z])$")
_TITLE = re.compile(r"PN:\s*(?P<pn>[A-Z0-9-]+)?(?:\s+REV:\s*(?P<rev>[A-Z0-9]+))?")
_BOM = re.compile(r"^(?P<item>\d+)\s*\|\s*(?P<pn>[A-Z0-9-]+)\s*\|\s*QTY\s+(?P<qty>-?\d+)$")


def parse(region_id: str, kind: RegionKind, text: str) -> Interpretation:
    t = " ".join(text.strip().upper().split())
    base = {"region_id": region_id, "kind": kind}
    try:
        if kind is RegionKind.FCF:
            parts = [p.strip() for p in t.split("|")]
            if parts[0] not in CHARACTERISTICS or len(parts) < 2:
                return Interpretation(**base, parse_ok=False)
            return Interpretation(
                **base,
                characteristic=parts[0],
                tolerance=float(parts[1]),
                datums=[p for p in parts[2:] if p],
            )
        if kind is RegionKind.DIMENSION:
            m = _DIM.match(t)
            if not m:
                return Interpretation(**base, parse_ok=False)
            return Interpretation(
                **base, nominal=float(m["nom"]), upper=float(m["up"]), lower=float(m["lo"])
            )
        if kind is RegionKind.DATUM:
            m = _DATUM.match(t)
            return (
                Interpretation(**base, datum_letter=m["l"])
                if m
                else Interpretation(**base, parse_ok=False)
            )
        if kind is RegionKind.TITLE_BLOCK:
            m = _TITLE.search(t)
            if not m:
                return Interpretation(**base, parse_ok=False)
            return Interpretation(**base, part_number=m["pn"], revision=m["rev"])
        if kind is RegionKind.BOM_ROW:
            m = _BOM.match(t)
            if not m:
                return Interpretation(**base, parse_ok=False)
            return Interpretation(
                **base, item=int(m["item"]), part_number=m["pn"], quantity=int(m["qty"])
            )
    except (ValueError, IndexError):
        pass
    return Interpretation(**base, parse_ok=False)
