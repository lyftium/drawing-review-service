"""Prometheus metrics. Labels never carry document content or file names."""

from __future__ import annotations

from prometheus_client import Counter, Gauge, Histogram

LATENCY_BUCKETS = (0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2, 5, 10, 30, 60)

REQUEST_LATENCY = Histogram(
    "drw_request_duration_seconds",
    "End-to-end request latency. Use histogram_quantile(0.95, ...) for p95.",
    ["route", "status"],
    buckets=LATENCY_BUCKETS,
)
STAGE_LATENCY = Histogram(
    "drw_stage_duration_seconds",
    "Latency per pipeline stage.",
    ["stage"],
    buckets=LATENCY_BUCKETS,
)
ERRORS = Counter("drw_errors_total", "Rejected or failed requests by error code.", ["code"])
FINDINGS = Counter("drw_findings_total", "Consistency findings raised.", ["rule_id", "severity"])
REGIONS = Counter("drw_regions_total", "Regions detected.", ["kind"])
INTERPRETER_FALLBACKS = Counter(
    "drw_interpreter_fallbacks_total", "VLM answers rejected by schema validation."
)
TTFT = Histogram(
    "drw_llm_time_to_first_token_seconds",
    "Time to first streamed token from the multimodal interpreter.",
    buckets=(0.05, 0.1, 0.25, 0.5, 1, 2, 5, 10),
)
BACKEND_READY = Gauge("drw_backend_ready", "1 when every backend reports ready.")
