# Demo — drawing review service

Run the public demonstrator locally. CPU stubs by default — no model weights required for tests.

## Prerequisites

- Python 3.10+, `make`
- Optional: Docker, Kind (for cluster smoke)

## Quickstart

```bash
make install
make test
make eval
make validate
```

**Expected:** unit/integration tests green; golden evaluation completes; manifests validate.

## Optional — Kind

If Docker and Kind are available:

```bash
make deploy-kind
./scripts/demo_rollback.sh
```

Evidence from a prior run: [`docs/evidence/kind-apply/`](evidence/kind-apply/). Image digest notes: [`docs/image-digests.md`](image-digests.md).

## Limitations

- Default path uses CPU stubs and synthetic drawings
- OpenShift AI / KServe manifests are prepared and schema-checked; **not** applied on a live GPU cluster
- Kind Ready ≠ production hardening
