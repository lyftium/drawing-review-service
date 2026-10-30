"""Stage 6: structuring and consistency checks.

These rules encode what a reviewer would check by hand. They are deliberately
simple and explainable: each finding names the rule and the regions involved, so
an engineer can confirm or dismiss it. Recognising a symbol correctly is not the
same as the drawing being correct, which is why these are scored separately.
"""

from __future__ import annotations

from collections import Counter

from .config import Settings
from .parsing import FORM, NEEDS_DATUM
from .schemas import Finding, Interpretation, RegionKind, Severity

RULES = {
    "R001": "Feature control frame references a datum that is not defined on the drawing.",
    "R002": "Form tolerance must not reference a datum.",
    "R003": "Orientation/location tolerance needs at least one datum reference.",
    "R004": "Geometric tolerance must be positive and within the plausible range.",
    "R005": "Dimension tolerance band is inverted or empty.",
    "R006": "Title block is missing the part number or revision.",
    "R007": "BOM quantity must be a positive integer.",
    "R008": "Duplicate BOM item number.",
    "R009": "Text could not be parsed for this region kind.",
}


def _f(rule: str, sev: Severity, ids: list[str], extra: str = "") -> Finding:
    return Finding(
        rule_id=rule,
        severity=sev,
        message=RULES[rule] + (f" {extra}" if extra else ""),
        region_ids=ids,
    )


def check_region(it: Interpretation, datums: set[str], settings: Settings) -> list[Finding]:
    out: list[Finding] = []
    rid = [it.region_id]
    if not it.parse_ok:
        return [_f("R009", Severity.WARNING, rid)]
    if it.kind is RegionKind.FCF:
        missing = [d for d in it.datums if d not in datums]
        if missing:
            out.append(_f("R001", Severity.ERROR, rid, f"Missing: {', '.join(missing)}."))
        if it.characteristic in FORM and it.datums:
            out.append(_f("R002", Severity.ERROR, rid))
        if it.characteristic in NEEDS_DATUM and not it.datums:
            out.append(_f("R003", Severity.ERROR, rid))
        if it.tolerance is None or not (0 < it.tolerance <= settings.max_tolerance_mm):
            out.append(_f("R004", Severity.ERROR, rid))
    elif it.kind is RegionKind.DIMENSION:
        if it.upper is None or it.lower is None or it.upper <= it.lower:
            out.append(_f("R005", Severity.ERROR, rid))
    elif it.kind is RegionKind.BOM_ROW:
        if it.quantity is None or it.quantity <= 0:
            out.append(_f("R007", Severity.ERROR, rid))
    return out


def check_document(
    items: list[Interpretation], settings: Settings
) -> tuple[dict[str, list[Finding]], list[Finding]]:
    datums = {i.datum_letter for i in items if i.kind is RegionKind.DATUM and i.datum_letter}
    per_region = {i.region_id: check_region(i, datums, settings) for i in items}

    doc: list[Finding] = []
    titles = [i for i in items if i.kind is RegionKind.TITLE_BLOCK and i.parse_ok]
    if not titles or not titles[0].part_number or not titles[0].revision:
        doc.append(_f("R006", Severity.ERROR, [t.region_id for t in titles]))

    counts = Counter(i.item for i in items if i.kind is RegionKind.BOM_ROW and i.item is not None)
    for item_no, n in counts.items():
        if n > 1:
            ids = [i.region_id for i in items if i.kind is RegionKind.BOM_ROW and i.item == item_no]
            doc.append(_f("R008", Severity.ERROR, ids, f"Item {item_no} appears {n} times."))
    return per_region, doc
