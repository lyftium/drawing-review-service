"""No drawing files in the repository: the golden drawings are generated from a seed."""

import json
import shutil
import subprocess

import pytest

from drawing_review.synth.golden import GoldenMismatch, ensure_images

from .conftest import GOLDEN

DRAWING_EXT = (".png", ".jpg", ".jpeg", ".tif", ".tiff", ".pdf", ".dxf", ".dwg", ".svg")


def test_no_drawing_files_are_tracked():
    out = subprocess.run(
        ["git", "ls-files"], cwd=GOLDEN.parent, capture_output=True, text=True, check=False
    )
    if out.returncode != 0:
        pytest.skip("not a git checkout")
    tracked = [f for f in out.stdout.splitlines() if f.lower().endswith(DRAWING_EXT)]
    assert tracked == []


def test_regeneration_matches_labels(tmp_path):
    for sub in ("labels", "expected"):
        shutil.copytree(GOLDEN / sub, tmp_path / sub)
    shutil.copy(GOLDEN / "manifest.json", tmp_path)
    imgs = ensure_images(tmp_path)
    assert [p.stem for p in imgs] == sorted(p.stem for p in (GOLDEN / "labels").glob("*.json"))
    assert (tmp_path / "images" / "syn-001.png").read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"


def test_tampered_labels_are_detected(tmp_path):
    shutil.copytree(GOLDEN / "labels", tmp_path / "labels")
    shutil.copy(GOLDEN / "manifest.json", tmp_path)
    p = tmp_path / "labels" / "syn-000.json"
    label = json.loads(p.read_text())
    label["defects"] = ["made-up"]
    p.write_text(json.dumps(label, indent=2))
    with pytest.raises(GoldenMismatch):
        ensure_images(tmp_path)
