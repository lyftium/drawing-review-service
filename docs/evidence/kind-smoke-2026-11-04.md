# Kind smoke — 2026-11-04 (America/Los_Angeles)

Environment: macOS Colima (vz) + Kind cluster `drw`. Docker Hub/GHCR pulls via host Privoxy `192.168.5.2:8118` (VM direct TCP egress refused under Tailscale/VZ NAT).

| Check | Result |
|---|---|
| `docker pull hello-world` / `python:3.11.10-slim-bookworm` / `ghcr.io/linuxcontainers/alpine:3.20` | **OK** after host-DNS + Privoxy |
| `kind create cluster --name drw` | **OK** (`kindest/node:v1.37.0`) — transcript in `kind-apply/` |
| `docker build` → `drawing-review:dev` | **OK** (local image id `sha256:612e1371c9c1951affc64153d6637bf70ba2792bf3779570fde1d81c3db656d2`) |
| `kind load` + `kubectl apply -k deploy/k8s/overlays/kind` | **OK** |
| Deploy Ready | **1/1 Available** — pod Running ready=true |
| Eval Job | **Failed** — `gates.yaml` missing from installed package (fixed in tree via package-data; rebuild needed) |
| GHCR push | **Blocked** — `gh` token scopes lack `write:packages` |

Transcripts: [`kind-apply/`](kind-apply/).
