# Kind smoke — 2026-11-04 (America/Los_Angeles)

Environment: local Kind cluster `drw` on a laptop VM. Image pulls used a local HTTP proxy because the VM could not reach the registries directly.

| Check | Result |
|---|---|
| Docker Hub + GHCR pulls | **OK** |
| `kind create --name drw` | **OK** (`kindest/node:v1.37.0`) |
| Build `drawing-review:dev` | **OK** — final image id `sha256:41505eb281baa06ee2a9efa4618e5a8358d1a2ee640af11b47e6ce2dcb72cd27` |
| Deploy Ready | **1/1 Available**, pod Running ready=true |
| Eval Job | **Complete 1/1** (after `package-data` includes `evaluation/gates.yaml`) |
| GHCR push / registry digest | **OK** via Actions — `sha256:77d1723b9d2a1a565ec8fa61787db5f881bf5a77156cfa7f4744b15c893b9bad` (RepoDigests verified) |

Transcripts under [`kind-apply/`](kind-apply/).

| Rollback demo | **OK** — `kubectl rollout undo` after annotation bump; image tag unchanged (`drawing-review:dev`); `/readyz` + `/healthz` OK — [rollback-20261104-183013.txt](kind-apply/rollback-20261104-183013.txt) |

