"""Materialise the golden drawings from code instead of committing image files.

The repository only stores the labels and the recorded pipeline outputs. The PNGs
are regenerated from the seed in ``golden/manifest.json`` and checked against the
committed labels, so a change in the generator (or in Pillow's font rendering) is
caught instead of silently producing a different reference set.
"""

from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path

from .generate import generate_set


class GoldenMismatch(RuntimeError):
    pass


def ensure_images(golden_dir: Path, *, force: bool = False) -> list[Path]:
    """Generate ``golden_dir/images`` if missing and verify it against the labels."""
    manifest = json.loads((golden_dir / "manifest.json").read_text())
    images = golden_dir / "images"
    expected = sorted(p.stem for p in (golden_dir / "labels").glob("*.json"))
    have = sorted(p.stem for p in images.glob("*.png")) if images.is_dir() else []
    if have == expected and not force:
        return sorted(images.glob("*.png"))

    with tempfile.TemporaryDirectory() as tmp:
        generate_set(Path(tmp), manifest["n"], manifest["seed"])
        for stem in expected:
            new = (Path(tmp) / "labels" / f"{stem}.json").read_text()
            if new != (golden_dir / "labels" / f"{stem}.json").read_text():
                raise GoldenMismatch(
                    f"regenerated {stem} does not match golden/labels/{stem}.json; the "
                    "generator or its font rendering changed. Re-record on purpose with "
                    "scripts/update_golden.py --regenerate."
                )
        images.mkdir(parents=True, exist_ok=True)
        for stem in expected:
            shutil.copyfile(Path(tmp) / "images" / f"{stem}.png", images / f"{stem}.png")
    return sorted(images.glob("*.png"))
