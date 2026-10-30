# Gateway in front of the service (proposed design)

This is a design, not something deployed in this repo. The manifests only assume
that callers arrive from an `ai-gateway` namespace (see the NetworkPolicy).

## Why a gateway

Several teams calling several AI services directly means every service reimplements
auth, quotas and logging, and nobody has one view of who uses what. One gateway in
front of the API and the inference servers gives that in one place.

## What it does

| Concern | Policy |
|---|---|
| Authentication | OIDC tokens from the company identity provider. No shared API keys. Service-to-service calls use their own client credentials. |
| Authorisation | Per team and per route: e.g. `analyze` for design engineers, raw `/v1/chat/completions` on vLLM only for the platform team. |
| Quotas | Requests per minute and concurrent requests per team. For LLM routes, a token budget per day as well, because one long prompt costs more than ten short ones. |
| Routing | `/drawing-review/*` to this API; `/llm/<model>/*` to the vLLM Service of that model. Canary weights for a new model version (e.g. 90/10), switched off by config, not by redeploying. |
| Timeouts and limits | Body size limit matching `DRW_MAX_UPLOAD_MB`; upstream timeout longer than the service's own, so the service reports the error, not the gateway. |
| Traceability | A request id is created at the gateway and passed as `x-request-id`; the API returns it and logs it, so one id follows a request end to end. |

## Logging policy

Documents can be sensitive, and logs are copied, shipped and kept far longer than
the documents. So, at every hop:

- **Logged**: timestamp, request id, caller identity (team / client id), route,
  status, latency, request and response sizes, model name and version, token
  counts, document sha256 prefix.
- **Never logged**: file names, file contents, page images, OCR text, prompts,
  model outputs, extracted values.
- vLLM runs with `--disable-log-requests` for the same reason.
- If content is ever needed to debug a case, it goes through the review tool with
  the owner's agreement, not through the logs.

## Options I would compare

Envoy-based gateways (Envoy AI Gateway, Kong, or the gateway that comes with the
platform, e.g. on OpenShift) all cover this list. The choice depends on what the
platform team already runs; adding a second gateway is rarely worth it.
