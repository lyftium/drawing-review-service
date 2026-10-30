import pytest
from pydantic import ValidationError

from drawing_review.config import Settings


def test_from_env_and_fingerprint_changes():
    a = Settings.from_env({})
    b = Settings.from_env({"DRW_MAX_PAGES": "5", "DRW_STUB_DROP_RATE": "0.1"})
    assert b.max_pages == 5 and b.stub_noise.drop_rate == 0.1
    assert a.fingerprint() != b.fingerprint()


def test_bad_config_fails_at_startup_not_at_request_time():
    with pytest.raises(ValidationError):
        Settings.from_env({"DRW_DETECTOR": "magic"})
    with pytest.raises(ValidationError):
        Settings.from_env({"DRW_STUB_DROP_RATE": "2"})
