# Laptop smoke — 2026-11-04T18:26:25Z

Environment: local macOS, Python 3.11, no cluster apply.

| Check | Result |
|---|---|
| `drawing-review-service` `pytest` | **57 passed** |
| `agent-gateway-stack` `pytest` | **48 passed** (includes prompt-injection posture) |
| `docker compose up --build` (AGS) | **Blocked** — `registry-1.docker.io` DNS refused in this environment |
| `kind create` / `make deploy-kind` | **Blocked** — same Docker Hub DNS for `kindest/node` |
| GHCR image push + digest | **Not run** — no base image pull possible here |

## Commands used

```bash
cd drawing-review-service && pip install -r requirements.lock -r requirements-dev.txt && pip install --no-deps -e . && pytest -q
cd agent-gateway-stack && pip install -e '.[dev]' && pytest -q
```

When Docker Hub is reachable: `make image`, `make deploy-kind`, `./scripts/demo_rollback.sh`, then paste transcripts beside this file.
