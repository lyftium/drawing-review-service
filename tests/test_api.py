"""Integration tests: the full HTTP path with stub backends, no network, no GPU."""


def test_health_and_readiness(client):
    assert client.get("/healthz").text == "ok"
    r = client.get("/readyz")
    assert r.status_code == 200 and r.json()["backends"]["detector"].startswith("stub")


def test_analyze_end_to_end(client, sample_png):
    r = client.post("/v1/analyze", files={"file": ("x.png", sample_png, "image/png")})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["summary"]["regions"] == len(body["items"]) > 0
    assert all(i["status"] == "pending_review" for i in body["items"])
    assert {"ingest", "detect", "ocr", "interpret", "checks"} <= body["timings_ms"].keys()
    assert body["lineage"]["config_hash"]
    assert r.headers["x-request-id"]


def test_csv_export(client, sample_png):
    r = client.post("/v1/analyze.csv", files={"file": ("x.png", sample_png, "image/png")})
    assert r.status_code == 200
    header = r.text.splitlines()[0]
    assert header.startswith("region_id,page,kind") and "reviewer_decision" in header


def test_wrong_type_is_415_with_request_id(client):
    r = client.post(
        "/v1/analyze",
        files={"file": ("d.png", b"GIF89a....", "image/png")},
        headers={"x-request-id": "abc123"},
    )
    assert r.status_code == 415
    assert r.json() == {
        "error": "unsupported_type",
        "detail": r.json()["detail"],
        "request_id": "abc123",
    }


def test_missing_file_field_is_422(client):
    r = client.post("/v1/analyze", data={"nope": "1"})
    assert r.status_code == 422 and r.json()["error"] == "invalid_request"


def test_metrics_exposed_without_document_content(client, sample_png):
    client.post("/v1/analyze", files={"file": ("secret-name.png", sample_png, "image/png")})
    m = client.get("/metrics").text
    assert "drw_request_duration_seconds_bucket" in m
    assert "drw_stage_duration_seconds_bucket" in m
    assert "secret-name" not in m and "SYN-" not in m


def test_logs_do_not_contain_document_text(client, sample_png, caplog):
    caplog.set_level("INFO", logger="drawing_review")
    client.post("/v1/analyze", files={"file": ("secret-name.png", sample_png, "image/png")})
    text = caplog.text
    assert "analyzed" in text
    assert "secret-name" not in text and "DATUM" not in text and "PN:" not in text


def test_not_ready_backend_returns_503(settings):
    from fastapi.testclient import TestClient

    from drawing_review.api import create_app
    from drawing_review.pipeline import Pipeline

    pipe = Pipeline(settings)
    pipe.backends.ocr.ready = lambda: False
    with TestClient(create_app(settings, pipe)) as c:
        assert c.get("/readyz").status_code == 503
        assert c.get("/healthz").status_code == 200  # alive, just not ready
