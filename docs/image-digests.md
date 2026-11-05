# Image digests (GHCR)

**Status.** Digests are recorded only after a successful `docker build` + `docker push` to `ghcr.io/lyftium/...`.

| Image | Tag | Digest | Built from | Date |
|---|---|---|---|---|
| `ghcr.io/lyftium/drawing-review-service` | `dev` / `sha-da178e9ec1c9` | _(not pushed — token lacks `write:packages`)_ | `Dockerfile` @ `da178e9ec1c9` local build id `sha256:612e1371c9c1951affc64153d6637bf70ba2792bf3779570fde1d81c3db656d2` | 2026-11-04 America/Los_Angeles |
| `ghcr.io/lyftium/agent-gateway-stack` | _(pending)_ | _(not pushed)_ | `Dockerfile` @ main | — |

## Local Kind build (not a registry digest)

| Field | Value |
|---|---|
| Local image | `drawing-review:dev` |
| Image ID | `sha256:612e1371c9c1951affc64153d6637bf70ba2792bf3779570fde1d81c3db656d2` |
| Git | `da178e9ec1c914635bc91ba53126f28ca91c284c` |
| Kind | cluster `drw`, deploy Ready 1/1 — see `docs/evidence/kind-apply/` |

## How to fill GHCR digests

```bash
gh auth refresh -h github.com -s write:packages,read:packages
echo "$(gh auth token)" | docker login ghcr.io -u lyftium --password-stdin
docker tag drawing-review:dev ghcr.io/lyftium/drawing-review-service:dev
docker push ghcr.io/lyftium/drawing-review-service:dev
docker inspect --format='{{index .RepoDigests 0}}' ghcr.io/lyftium/drawing-review-service:dev
```

Until a row has a real registry `sha256:…` from `RepoDigests`, treat GHCR references as **prepared**, not released artefacts.
