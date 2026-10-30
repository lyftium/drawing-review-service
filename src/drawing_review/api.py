"""HTTP interface.

Logging policy: we log the request id, the document sha256 prefix, sizes, timings
and error codes. We never log file names, extracted text or images, because the
documents can be sensitive and logs travel further than the documents do.
"""

from __future__ import annotations

import logging
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, Request, UploadFile
from fastapi.concurrency import run_in_threadpool
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, PlainTextResponse, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from . import __version__
from .config import Settings
from .ingest import IngestError
from .metrics import BACKEND_READY, ERRORS, REQUEST_LATENCY
from .pipeline import Pipeline
from .review import to_csv
from .schemas import AnalysisResult, ErrorBody

log = logging.getLogger("drawing_review")


def create_app(settings: Settings | None = None, pipeline: Pipeline | None = None) -> FastAPI:
    state: dict[str, Pipeline] = {}

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Load models once at startup; the startup probe waits for this.
        state["pipeline"] = pipeline or Pipeline(settings or Settings.from_env())
        BACKEND_READY.set(1 if state["pipeline"].backends.ready() else 0)
        yield
        state.clear()

    app = FastAPI(title="drawing-review", version=__version__, lifespan=lifespan)

    @app.middleware("http")
    async def timing(request: Request, call_next):
        rid = request.headers.get("x-request-id") or uuid.uuid4().hex[:16]
        request.state.rid = rid
        t0 = time.perf_counter()
        response = await call_next(request)
        route = request.scope.get("route")
        REQUEST_LATENCY.labels(
            route=getattr(route, "path", "unmatched"), status=str(response.status_code)
        ).observe(time.perf_counter() - t0)
        response.headers["x-request-id"] = rid
        return response

    def error(request: Request, status: int, code: str, detail: str) -> JSONResponse:
        ERRORS.labels(code=code).inc()
        body = ErrorBody(error=code, detail=detail, request_id=request.state.rid)
        log.warning("request_failed rid=%s code=%s status=%d", request.state.rid, code, status)
        return JSONResponse(status_code=status, content=body.model_dump())

    @app.exception_handler(IngestError)
    async def ingest_error(request: Request, exc: IngestError):
        return error(request, exc.status, exc.code, exc.detail)

    @app.exception_handler(RequestValidationError)
    async def validation_error(request: Request, exc: RequestValidationError):
        return error(request, 422, "invalid_request", "Expected multipart field 'file'.")

    @app.exception_handler(Exception)
    async def unhandled(request: Request, exc: Exception):
        log.exception("unhandled rid=%s", request.state.rid)
        return error(request, 500, "internal_error", "Unexpected error. Quote the request id.")

    @app.get("/healthz", response_class=PlainTextResponse)
    async def healthz():
        # Liveness: the process is up and the event loop answers. Nothing more.
        return "ok"

    @app.get("/readyz")
    async def readyz(request: Request):
        p = state.get("pipeline")
        ok = bool(p and p.backends.ready())
        BACKEND_READY.set(1 if ok else 0)
        if not ok:
            return error(request, 503, "not_ready", "Backends are not ready.")
        return {"status": "ready", "backends": p.backends.describe()}

    @app.get("/metrics")
    async def metrics():
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

    @app.get("/v1/version")
    async def version():
        return state["pipeline"].lineage()

    async def _run(request: Request, file: UploadFile) -> AnalysisResult:
        p = state["pipeline"]
        data = await file.read(int(p.settings.max_upload_mb * 1024 * 1024) + 1)
        result = await run_in_threadpool(p.analyze_bytes, data)
        log.info(
            "analyzed rid=%s doc=%s bytes=%d regions=%d errors=%d ms=%.1f",
            request.state.rid,
            result.document_id[:12],
            len(data),
            result.summary["regions"],
            result.summary["errors"],
            sum(result.timings_ms.values()),
        )
        return result

    @app.post(
        "/v1/analyze",
        response_model=AnalysisResult,
        responses={413: {"model": ErrorBody}, 415: {"model": ErrorBody}, 422: {"model": ErrorBody}},
    )
    async def analyze(request: Request, file: UploadFile = File(...)):
        return await _run(request, file)

    @app.post("/v1/analyze.csv", response_class=PlainTextResponse)
    async def analyze_csv(request: Request, file: UploadFile = File(...)):
        return PlainTextResponse(to_csv(await _run(request, file)), media_type="text/csv")

    return app


def app_factory() -> FastAPI:  # uvicorn --factory drawing_review.api:app_factory
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    return create_app()
