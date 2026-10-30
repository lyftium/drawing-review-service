import pytest

from drawing_review.parsing import parse
from drawing_review.schemas import RegionKind


@pytest.mark.parametrize(
    "text,char,tol,datums",
    [
        ("POS|0.10|A|B", "POS", 0.10, ["A", "B"]),
        ("FLAT|0.05", "FLAT", 0.05, []),
        ("  perp | 0.02 | a ", "PERP", 0.02, ["A"]),
    ],
)
def test_fcf(text, char, tol, datums):
    it = parse("r", RegionKind.FCF, text)
    assert it.parse_ok and it.characteristic == char and it.tolerance == tol
    assert it.datums == datums


@pytest.mark.parametrize("text", ["XYZ|0.1|A", "POS", "POS|abc|A", ""])
def test_fcf_garbage_is_flagged_not_guessed(text):
    assert parse("r", RegionKind.FCF, text).parse_ok is False


def test_dimension():
    it = parse("r", RegionKind.DIMENSION, "DIA 8.00 +0.02/-0.02")
    assert (it.nominal, it.upper, it.lower) == (8.0, 0.02, -0.02)


def test_title_without_revision():
    it = parse("r", RegionKind.TITLE_BLOCK, "PN: SYN-1234")
    assert it.part_number == "SYN-1234" and it.revision is None


def test_bom_row():
    it = parse("r", RegionKind.BOM_ROW, "3 | PRT-100 | QTY 4")
    assert (it.item, it.part_number, it.quantity) == (3, "PRT-100", 4)
