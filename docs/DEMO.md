# Demo — drawing review service

Run the public demonstrator locally. CPU stubs by default — no model weights required for tests.

## Prerequisites

- Python 3.11+, `make`
- `make validate` also needs `kubectl` and `kubeconform`
- Optional: Docker and Kind, for the cluster smoke

## Quickstart

```bash
make install
make test
make eval
make validate
```

`make eval` generates synthetic drawings under `golden/` and runs the gates.

**Expected:** tests pass, the golden evaluation finishes, and manifest validation prints no errors.

## Optional — Kind

If Docker and Kind are available:

```bash
make deploy-kind
./scripts/demo_rollback.sh
```

Evidence from a prior run: [`docs/evidence/kind-apply/`](evidence/kind-apply/). Image digest notes: [`docs/image-digests.md`](image-digests.md).

## Limitations

CPU stubs and synthetic drawings only. Kind shows the manifests apply locally. The OpenShift AI / KServe files are schema-checked and have not been applied on a GPU cluster.
