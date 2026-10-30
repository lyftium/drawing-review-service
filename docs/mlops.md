# Versioning, evaluation and release

## What is recorded for every result

| What | Where it comes from |
|---|---|
| Code version | `git_sha`, baked into the image as `DRW_GIT_SHA` at build time |
| Model / backend versions | each backend's `version` string (e.g. weights file name) |
| Configuration | `config_hash`, a hash of the full validated settings |
| Data | `dataset_hash` over the labels and images of the evaluation set |

Every API response carries the first three in `lineage`. Every evaluation run
writes a JSON record with all four plus the scores (`runs/`), so any number can be
traced back to exactly what produced it.

## Three kinds of checks, kept separate

1. **Software tests** (`pytest`): the code does what it says. Run on every commit.
2. **Model evaluation** (`drawing-review eval`): extraction quality on the reference set.
3. **Business acceptance**: does the review raise the problems a checker would raise,
   and stay quiet on clean drawings? Also from the harness, gated separately.

## Release path

```
code + model version
  -> software tests (CI)
  -> evaluation on the reference set, gates in gates.yaml (CI, then the eval Job on the cluster for real weights)
  -> image build, tagged with the git sha
  -> validation in a test namespace
  -> rollout (RollingUpdate, maxUnavailable 0) and monitoring
  -> rollback: kubectl rollout undo, or point the PVC/config back to the previous weights
```

After release, reviewers' decisions in the CSV (`reviewer_decision`) are the
feedback that grows the reference set. A disagreement between the review and the
engineer becomes a new labelled case, not just a ticket.
