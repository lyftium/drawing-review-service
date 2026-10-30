from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from drawing_review.api import create_app
from drawing_review.config import Settings

GOLDEN = Path(__file__).resolve().parents[1] / "golden"


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
