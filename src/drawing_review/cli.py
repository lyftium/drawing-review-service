"""Command line: ``drawing-review synth | golden | analyze | eval``."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .config import Settings


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="drawing-review")
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("synth", help="generate synthetic drawings with ground truth")
    s.add_argument("--out", type=Path, required=True)
    s.add_argument("-n", type=int, default=12)
    s.add_argument("--seed", type=int, default=7)

    g = sub.add_parser("golden", help="generate and verify the golden drawings from their seed")
    g.add_argument("--dir", type=Path, default=Path("golden"))

    a = sub.add_parser("analyze", help="analyze one file and print JSON")
    a.add_argument("path", type=Path)

    e = sub.add_parser("eval", help="run the evaluation harness on a labelled set")
    e.add_argument("--data", type=Path, required=True)
    e.add_argument("--report", type=Path, default=None)
    e.add_argument("--runs-dir", type=Path, default=Path("runs"))

    args = ap.parse_args(argv)
    settings = Settings.from_env()

    if args.cmd == "synth":
        from .synth.generate import generate_set

        paths = generate_set(args.out, args.n, args.seed)
        print(f"wrote {len(paths)} drawings to {args.out}")
    elif args.cmd == "golden":
        from .synth.golden import ensure_images

        print(f"{len(ensure_images(args.dir))} golden drawings ready in {args.dir}/images")
    elif args.cmd == "analyze":
        from .pipeline import Pipeline

        res = Pipeline(settings).analyze_bytes(args.path.read_bytes())
        print(res.model_dump_json(indent=2))
    elif args.cmd == "eval":
        from .evaluation.harness import evaluate, render_markdown

        if (args.data / "manifest.json").exists():
            from .synth.golden import ensure_images

            ensure_images(args.data)
        report = evaluate(args.data, settings, runs_dir=args.runs_dir)
        md = render_markdown(report)
        if args.report:
            args.report.parent.mkdir(parents=True, exist_ok=True)
            args.report.write_text(md)
        print(md)
        print(json.dumps(report["gates"], indent=2), file=sys.stderr)
        return 0 if report["gates"]["passed"] else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
