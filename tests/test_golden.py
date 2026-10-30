"""Regression: the pipeline must reproduce the recorded golden outputs exactly."""

import json

import pytest

from drawing_review.config import Settings
from drawing_review.pipeline import Pipeline
from drawing_review.snapshot import snapshot

from .conftest import GOLDEN

IMAGES = sorted((GOLDEN / "images").glob("*.png"))


@pytest.fixture(scope="module")
def pipe():
    return Pipeline(Settings())


@pytest.mark.parametrize("img", IMAGES, ids=[p.stem for p in IMAGES])
def test_matches_golden(pipe, img):
    expected = json.loads((GOLDEN / "expected" / f"{img.stem}.json").read_text())
    assert snapshot(pipe.analyze_bytes(img.read_bytes())) == expected


def test_golden_set_is_not_empty():
    assert len(IMAGES) >= 10
