# Observability triad (service · model quality · infra)

Three different questions — do not mix their dashboards.

| Layer | Question | What this repo exports / documents |
|---|---|---|
| **Service** | Is the API healthy and fast enough? | Prometheus: `drw_request_latency_seconds`, `drw_stage_latency_seconds`, `drw_errors_total`, `/healthz` `/readyz` |
| **Model quality** | Is extraction still acceptable? | Offline: `make eval` + `gates.yaml`. Online quality probe is **not** automated here — re-run golden after weight/config change |
| **Infra** | GPU / node / pull / schedule | Runbook events-first (`docs/runbook.md`). No fake DCGM series in this demo |

## TTFT

`drw_ttft_seconds` (via interpreter client) records time-to-first-token when talking to an OpenAI-compatible VLM. Stub/rules backends do not emit meaningful TTFT.

## What is not claimed

- No production Grafana board URL.
- No cluster-scraped metrics until something is actually applied.
- Serving-lab numbers live in [vllm-serving-benchmark-t4](https://github.com/lyftium/vllm-serving-benchmark-t4), not here.
