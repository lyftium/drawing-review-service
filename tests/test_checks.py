from drawing_review.checks import check_document
from drawing_review.config import Settings
from drawing_review.parsing import parse
from drawing_review.schemas import RegionKind as K


def rules(*regions):
    items = [parse(f"r{i}", k, t) for i, (k, t) in enumerate(regions)]
    per, doc = check_document(items, Settings())
    return sorted({f.rule_id for fs in per.values() for f in fs} | {f.rule_id for f in doc})


TITLE = (K.TITLE_BLOCK, "PN: SYN-1 REV: A")
DATUM_A = (K.DATUM, "DATUM A")


def test_clean_drawing_raises_nothing():
    assert (
        rules(
            TITLE,
            DATUM_A,
            (K.FCF, "POS|0.10|A"),
            (K.DIMENSION, "10.00 +0.05/-0.05"),
            (K.BOM_ROW, "1 | P-1 | QTY 2"),
        )
        == []
    )


def test_undefined_datum():
    assert rules(TITLE, DATUM_A, (K.FCF, "POS|0.10|A|D")) == ["R001"]


def test_form_tolerance_with_datum():
    assert rules(TITLE, DATUM_A, (K.FCF, "FLAT|0.05|A")) == ["R002"]


def test_location_without_datum():
    assert rules(TITLE, (K.FCF, "POS|0.10")) == ["R003"]


def test_zero_and_implausible_tolerance():
    assert rules(TITLE, DATUM_A, (K.FCF, "PERP|0.00|A")) == ["R004"]
    assert rules(TITLE, DATUM_A, (K.FCF, "PERP|9.00|A")) == ["R004"]


def test_inverted_band():
    assert rules(TITLE, (K.DIMENSION, "10.00 -0.05/+0.05")) == ["R005"]


def test_missing_revision_and_missing_title():
    assert rules((K.TITLE_BLOCK, "PN: SYN-1")) == ["R006"]
    assert rules(DATUM_A) == ["R006"]


def test_bom_quantity_and_duplicates():
    assert rules(TITLE, (K.BOM_ROW, "1 | P-1 | QTY 0")) == ["R007"]
    assert rules(TITLE, (K.BOM_ROW, "1 | P-1 | QTY 1"), (K.BOM_ROW, "1 | P-2 | QTY 1")) == ["R008"]


def test_unparseable_text_is_a_warning():
    assert rules(TITLE, (K.FCF, "???")) == ["R009"]
