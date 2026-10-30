"""Small load benchmark.

Two modes:

  service  POST golden drawings to /v1/analyze at a fixed concurrency and report
           latency percentiles, throughput and error rate.
  llm      Stream chat completions from an OpenAI-compatible endpoint (vLLM) and
           report time to first token, end-to-end latency and output tokens/s.

Examples:

  python bench/load_test.py service --url http://localhost:8080 -n 200 -c 8
  python bench/load_test.py llm --url http://localhost:8000/v1 --model <name> -n 50 -c 4

Results depend entirely on the machine, the backends and the inputs. Record them
together with the lineage block that the script prints, or don't record them.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import statistics
import time
from pathlib import Path

import httpx

GOLDEN = Path(__file__).resolve().parents[1] / "golden" / "images"  # `drawing-review golden` first


def pct(values: list[float], q: float) -> float:
    if not values:
        return float("nan")
    s = sorted(values)
    k = max(0, min(len(s) - 1, round(q / 100 * (len(s) - 1))))
    return s[k]


async def run_service(url: str, n: int, c: int) -> dict:
    files = [p.read_bytes() for p in sorted(GOLDEN.glob("*.png"))]
    lat, errors = [], 0
    sem = asyncio.Semaphore(c)
    async with httpx.AsyncClient(timeout=60) as client:
        version = (await client.get(f"{url}/v1/version")).json()

        async def one(i: int):
            nonlocal errors
            async with sem:
                t0 = time.perf_counter()
                try:
                    r = await client.post(
                        f"{url}/v1/analyze",
                        files={"file": ("d.png", files[i % len(files)], "image/png")},
                    )
                    ok = r.status_code == 200
                except httpx.HTTPError:
                    ok = False
                lat.append(time.perf_counter() - t0)
                errors += not ok

        t0 = time.perf_counter()
        await asyncio.gather(*(one(i) for i in range(n)))
        wall = time.perf_counter() - t0
    return {
        "mode": "service",
        "requests": n,
        "concurrency": c,
        "error_rate": round(errors / n, 4),
        "throughput_rps": round(n / wall, 2),
        "latency_ms": {
            "p50": round(pct(lat, 50) * 1000, 1),
            "p95": round(pct(lat, 95) * 1000, 1),
            "p99": round(pct(lat, 99) * 1000, 1),
            "mean": round(statistics.fmean(lat) * 1000, 1),
        },
        "lineage": version,
    }


async def run_llm(url: str, model: str, n: int, c: int, max_tokens: int) -> dict:
    prompt = "Explain in two sentences what a datum reference frame is on a drawing."
    ttft, lat, tps, errors = [], [], [], 0
    sem = asyncio.Semaphore(c)
    async with httpx.AsyncClient(timeout=120) as client:

        async def one():
            nonlocal errors
            async with sem:
                body = {
                    "model": model,
                    "stream": True,
                    "max_tokens": max_tokens,
                    "temperature": 0,
                    "messages": [{"role": "user", "content": prompt}],
                }
                t0, first, chunks = time.perf_counter(), None, 0
                try:
                    async with client.stream("POST", f"{url}/chat/completions", json=body) as r:
                        r.raise_for_status()
                        async for line in r.aiter_lines():
                            if not line.startswith("data: ") or line == "data: [DONE]":
                                continue
                            delta = json.loads(line[6:])["choices"][0]["delta"].get("content")
                            if delta:
                                first = first or time.perf_counter()
                                chunks += 1
                except (httpx.HTTPError, KeyError, json.JSONDecodeError):
                    errors += 1
                    return
                end = time.perf_counter()
                if first:
                    ttft.append(first - t0)
                    if end > first:
                        tps.append(chunks / (end - first))
                lat.append(end - t0)

        t0 = time.perf_counter()
        await asyncio.gather(*(one() for _ in range(n)))
        wall = time.perf_counter() - t0
    return {
        "mode": "llm",
        "model": model,
        "requests": n,
        "concurrency": c,
        "max_tokens": max_tokens,
        "error_rate": round(errors / n, 4),
        "throughput_rps": round(n / wall, 2),
        "ttft_ms": {"p50": round(pct(ttft, 50) * 1000, 1), "p95": round(pct(ttft, 95) * 1000, 1)},
        "latency_ms": {"p50": round(pct(lat, 50) * 1000, 1), "p95": round(pct(lat, 95) * 1000, 1)},
        # stream chunks per second, roughly tokens/s per request for vLLM
        "output_chunks_per_s_p50": round(pct(tps, 50), 1),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["service", "llm"])
    ap.add_argument("--url", required=True)
    ap.add_argument("--model", default="")
    ap.add_argument("-n", type=int, default=100)
    ap.add_argument("-c", type=int, default=4)
    ap.add_argument("--max-tokens", type=int, default=128)
    a = ap.parse_args()
    if a.mode == "service":
        res = asyncio.run(run_service(a.url.rstrip("/"), a.n, a.c))
    else:
        res = asyncio.run(run_llm(a.url.rstrip("/"), a.model, a.n, a.c, a.max_tokens))
    print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
