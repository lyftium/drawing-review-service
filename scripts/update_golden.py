"""Re-record the golden expectations.

Run this only when a change in behaviour is intended, and explain the diff in the
pull request. The regression test fails on any unexplained difference.

    python scripts/update_golden.py               # re-record expected outputs
    python scripts/update_golden.py --regenerate  # also rewrite labels from the seed
"""

import json
import sys
import tempfile
from pathlib import Path

from drawing_review.config import Settings
from drawing_review.pipeline import Pipeline
from drawing_review.snapshot import snapshot
from drawing_review.synth.generate import generate_set
from drawing_review.synth.golden import ensure_images

ROOT = Path(__file__).resolve().parents[1] / "golden"

if "--regenerate" in sys.argv:
    m = json.loads((ROOT / "manifest.json").read_text())
    with tempfile.TemporaryDirectory() as tmp:
        generate_set(Path(tmp), m["n"], m["seed"])
        for f in sorted((Path(tmp) / "labels").glob("*.json")):
            (ROOT / "labels" / f.name).write_text(f.read_text())
ensure_images(ROOT, force=True)

pipe = Pipeline(Settings())
for img in sorted((ROOT / "images").glob("*.png")):
    snap = snapshot(pipe.analyze_bytes(img.read_bytes()))
    (ROOT / "expected" / f"{img.stem}.json").write_text(json.dumps(snap, indent=2) + "\n")
    print("recorded", img.name)
