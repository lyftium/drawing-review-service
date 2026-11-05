# Image digests (GHCR)

**Status.** Registry digests only after `docker push` to `ghcr.io/lyftium/...`.

| Image | Tag | Digest | Built from | Date |
|---|---|---|---|---|
| `ghcr.io/lyftium/drawing-review-service` | `dev` (intended) | _(not pushed — need `write:packages`)_ | local Kind build | 2026-11-04 America/Los_Angeles |
| `ghcr.io/lyftium/agent-gateway-stack` | _(pending)_ | _(not pushed)_ | — | — |

## Local Kind build (image id, not a registry digest)

| Field | Value |
|---|---|
| Local tag | `drawing-review:dev` |
| Image ID | `sha256:41505eb281baa06ee2a9efa4618e5a8358d1a2ee640af11b47e6ce2dcb72cd27` |
| Kind | `drw` — deploy Ready 1/1 + eval Job Complete |

```bash
gh auth refresh -h github.com -s write:packages,read:packages
echo "$(gh auth token)" | docker login ghcr.io -u lyftium --password-stdin
docker tag drawing-review:dev ghcr.io/lyftium/drawing-review-service:dev
docker push ghcr.io/lyftium/drawing-review-service:dev
docker inspect --format='{{index .RepoDigests 0}}' ghcr.io/lyftium/drawing-review-service:dev
```
