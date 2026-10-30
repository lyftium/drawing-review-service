from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from drawing_review.api import create_app
from drawing_review.config import Settings
from drawing_review.synth.golden import ensure_images

GOLDEN = Path(__file__).resolve().parents[1] / "golden"
# The drawings are not committed: build them from the seed before collection.
ensure_images(GOLDEN)


@pytest.fixture
def golden_dir() -> Path:
    return GOLDEN


@pytest.fixture
def settings() -> Settings:
    return Settings()


@pytest.fixture
def client(settings):
    with TestClient(create_app(settings)) as c:
        yield c


@pytest.fixture
def sample_png(golden_dir) -> bytes:
    return (golden_dir / "images" / "syn-001.png").read_bytes()
