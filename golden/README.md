# Golden reference set

Twelve **synthetic** drawings made by `drawing-review synth --out golden -n 12 --seed 7`.
Nothing here comes from a real drawing or a real part.

- `images/`: the PNGs (ground-truth annotations are embedded for the stub backends)
- `labels/`: regions, text and seeded defects, used by the evaluation harness
- `expected/`: recorded pipeline output, used by `tests/test_golden.py`

The point of this folder is simple: refactors must not change results by accident.
If a change is intended, re-record with `python scripts/update_golden.py` and explain
the diff in the PR.
