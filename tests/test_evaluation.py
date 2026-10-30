from drawing_review.config import Settings, StubNoise
from drawing_review.evaluation.harness import apply_gates, evaluate
from drawing_review.evaluation.metrics import cer, levenshtein, match_boxes, prf
from drawing_review.schemas import BBox


def test_levenshtein_and_cer():
    assert levenshtein("kitten", "sitting") == 3
    assert cer("POS|0.10|A", "POS|0.10|A") == 0


def test_box_matching_is_one_to_one_and_kind_aware():
    b = BBox(x0=0, y0=0, x1=10, y1=10)
    pred = [("p1", "fcf", b), ("p2", "fcf", b), ("p3", "datum", b)]
    truth = [("t1", "fcf", b)]
    assert match_boxes(pred, truth) == [("p2", "t1")] or match_boxes(pred, truth) == [("p1", "t1")]


def test_prf_edge_cases():
    assert prf(0, 0, 0)["f1"] == 0.0


def test_gate_logic():
    rep = {"a": {"b": 0.8}}
    assert not apply_gates(rep, {"gates": [{"metric": "a.b", "min": 0.9}]})["passed"]
    assert apply_gates(rep, {"gates": [{"metric": "a.b", "max": 0.9}]})["passed"]


def test_clean_backends_pass_gates_and_record_lineage(golden_dir, tmp_path):
    rep = evaluate(golden_dir, Settings(), runs_dir=tmp_path)
    assert rep["gates"]["passed"]
    run = next(tmp_path.glob("*.json")).read_text()
    for key in ("git_sha", "config_hash", "dataset_hash", "backends"):
        assert key in run


def test_extraction_and_business_scores_diverge_under_noise(golden_dir):
    """Small reading errors can look fine on extraction metrics and still break the review."""
    noisy = Settings(stub_noise=StubNoise(char_error_rate=0.03, drop_rate=0.05, jitter_px=4))
    rep = evaluate(golden_dir, noisy)
    assert rep["extraction"]["detection"]["recall"] >= 0.9
    assert rep["extraction"]["ocr_cer"] <= 0.05
    assert not rep["gates"]["passed"]  # business gates catch it
