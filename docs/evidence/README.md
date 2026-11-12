# Evidence

Start here after the [Demo](../DEMO.md). This index distinguishes recorded results from implementation scope.

| File | What it records | Boundary |
|---|---|---|
| [`laptop-smoke-2026-11-04.md`](laptop-smoke-2026-11-04.md) | Local CPU test run | No real model or GPU inference |
| [`kubeconform-2026-11-04.md`](kubeconform-2026-11-04.md) | Rendered manifest validation | Schema checks are not a cluster apply |
| [`kind-smoke-2026-11-04.md`](kind-smoke-2026-11-04.md) | Local Kind build, readiness, evaluation Job, image digest, and rollback | Stub backends on a local cluster |
| [`kind-apply/`](kind-apply/) | Transcripts behind the Kind smoke summary | Includes the initial evaluation packaging failure and subsequent successful run |
| [`RELEASE-PACK.md`](RELEASE-PACK.md) | Index of implementation and recorded release checks | Not a deployment approval |

Public CI configuration is at [`.github/workflows/ci.yml`](../../.github/workflows/ci.yml); the latest status is visible in the README badge and Actions tab. Test counts and statuses belong to the run at that commit rather than this static index.

Do not add undocumented timings, digests, or model metrics. The public golden set is synthetic; a passing software gate is not evidence of production drawing quality.
