"""Scoring functions. Kept free of I/O so they can be unit-tested on tiny inputs."""

from __future__ import annotations

from ..schemas import BBox


def levenshtein(a: str, b: str) -> int:
    if len(a) < len(b):
        a, b = b, a
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def cer(pred: str, truth: str) -> float:
    return levenshtein(pred, truth) / max(len(truth), 1)


def match_boxes(
    pred: list[tuple[str, str, BBox]], truth: list[tuple[str, str, BBox]], iou_min: float = 0.5
) -> list[tuple[str, str]]:
    """Greedy one-to-one matching by IoU within the same kind. Returns (pred_id, truth_id)."""
    pairs = []
    for pid, pk, pb in pred:
        for tid, tk, tb in truth:
            if pk == tk:
                iou = pb.iou(tb)
                if iou >= iou_min:
                    pairs.append((iou, pid, tid))
    pairs.sort(reverse=True)
    used_p, used_t, out = set(), set(), []
    for _, pid, tid in pairs:
        if pid not in used_p and tid not in used_t:
            used_p.add(pid)
            used_t.add(tid)
            out.append((pid, tid))
    return out


def prf(tp: int, fp: int, fn: int) -> dict[str, float]:
    p = tp / (tp + fp) if tp + fp else 0.0
    r = tp / (tp + fn) if tp + fn else 0.0
    f = 2 * p * r / (p + r) if p + r else 0.0
    return {
        "precision": round(p, 4),
        "recall": round(r, 4),
        "f1": round(f, 4),
        "tp": tp,
        "fp": fp,
        "fn": fn,
    }
