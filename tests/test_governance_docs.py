"""Governance / rollback artefacts exist for screeners — content checked elsewhere."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_governance_and_rollback_docs_present():
    required = [
        "docs/model-card.md",
        "docs/data-card.md",
        "docs/risk-register.md",
        "docs/ai-act-mapping.md",
        "docs/rollback.md",
        "scripts/demo_rollback.sh",
        "docs/evidence/laptop-smoke-2026-11-04.md",
        "ci/github-actions-ci.yml",
        "scripts/install-github-actions.sh",
    ]
    missing = [p for p in required if not (ROOT / p).is_file()]
    assert not missing, f"missing: {missing}"
