"""Lineage: enough to reproduce any result later.

Every analysis and every evaluation run records the code version, the backend
(model) versions, the configuration fingerprint and, for evaluations, a hash of the
dataset manifest.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess  # noqa: S404
from datetime import UTC, datetime
from pathlib import Path

from . import __version__


def git_sha() -> str:
    env = os.environ.get("DRW_GIT_SHA")  # baked into the image at build time
    if env:
        return env
    try:
        out = subprocess.run(  # noqa: S603
            ["git", "rev-parse", "--short=12", "HEAD"],  # noqa: S607
            capture_output=True,
            text=True,
            timeout=2,
            check=False,
        )
        return out.stdout.strip() or "unknown"
    except (OSError, subprocess.SubprocessError):
        return "unknown"


def dataset_hash(paths: list[Path]) -> str:
    h = hashlib.sha256()
    for p in sorted(paths):
        h.update(p.name.encode())
        h.update(hashlib.sha256(p.read_bytes()).digest())
    return h.hexdigest()[:16]


def run_record(
    kind: str,
    *,
    config_hash: str,
    backends: dict[str, str],
    dataset: str | None = None,
    extra: dict | None = None,
) -> dict:
    return {
        "kind": kind,
        "timestamp": datetime.now(UTC).isoformat(timespec="seconds"),
        "service_version": __version__,
        "git_sha": git_sha(),
        "config_hash": config_hash,
        "backends": backends,
        "dataset_hash": dataset,
        **(extra or {}),
    }


def write_run(record: dict, runs_dir: Path) -> Path:
    runs_dir.mkdir(parents=True, exist_ok=True)
    stamp = record["timestamp"].replace(":", "").replace("-", "")
    path = runs_dir / f"{stamp}-{record['kind']}-{record['git_sha']}.json"
    path.write_text(json.dumps(record, indent=2, sort_keys=True))
    return path
