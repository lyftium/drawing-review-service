# Golden reference set

Twelve **synthetic** drawings, generated from the seed in `manifest.json`.
Nothing here comes from a real drawing or a real part, and no image is committed.

- `images/`: created on demand by `drawing-review golden` (and automatically by the tests,
  `drawing-review eval` and the Docker build). The generated PNGs are checked against
  `labels/`, so a change in the generator is caught. Git-ignored.
- `manifest.json`: generator, count and seed
- `labels/`: regions, text and seeded defects, used by the evaluation harness
- `expected/`: recorded pipeline output, used by `tests/test_golden.py`

The point of this folder is simple: refactors must not change results by accident.
If a change is intended, re-record with `python scripts/update_golden.py` (add
`--regenerate` if the generator itself changed) and explain
the diff in the PR.
