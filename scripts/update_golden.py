"""Re-record the golden expectations.

Run this only when a change in behaviour is intended, and explain the diff in the
pull request. The regression test fails on any unexplained difference.

    python scripts/update_golden.py
"""

import json
from pathlib import Path

from drawing_review.config import Settings
from drawing_review.pipeline import Pipeline
from drawing_review.snapshot import snapshot

ROOT = Path(__file__).resolve().parents[1] / "golden"

pipe = Pipeline(Settings())
for img in sorted((ROOT / "images").glob("*.png")):
    snap = snapshot(pipe.analyze_bytes(img.read_bytes()))
    (ROOT / "expected" / f"{img.stem}.json").write_text(json.dumps(snap, indent=2) + "\n")
    print("recorded", img.name)
