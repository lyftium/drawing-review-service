"""Synthetic engineering drawings with ground truth.

Everything here is made up: part numbers, geometry and tolerances are random. No
real drawing, customer data or proprietary format is used. Each drawing gets:

* a PNG with a border, a part outline, datum labels, feature control frames,
  dimensions, a BOM table and a title block;
* the region annotations, both in a PNG text chunk (read by the stub backends) and
  in ``labels/<name>.json`` (read by the evaluation harness);
* zero to two *seeded defects*, recorded with the rule a reviewer should raise.
  The defect list is written by the generator from what it inserted, independently
  of ``checks.py``, so the harness really tests the rules engine.
"""

from __future__ import annotations

import json
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from PIL.PngImagePlugin import PngInfo

W, H = 1400, 1000
DEFECTS = [
    "missing_datum_ref",
    "form_with_datum",
    "location_without_datum",
    "zero_tolerance",
    "inverted_band",
    "missing_revision",
    "zero_qty",
    "duplicate_item",
]
DEFECT_RULE = {
    "missing_datum_ref": "R001",
    "form_with_datum": "R002",
    "location_without_datum": "R003",
    "zero_tolerance": "R004",
    "inverted_band": "R005",
    "missing_revision": "R006",
    "zero_qty": "R007",
    "duplicate_item": "R008",
}


def _font(size: int = 18) -> ImageFont.ImageFont:
    try:
        return ImageFont.load_default(size=size)
    except TypeError:  # very old Pillow
        return ImageFont.load_default()


class _Sheet:
    def __init__(self, name: str):
        self.name = name
        self.img = Image.new("L", (W, H), 255)
        self.d = ImageDraw.Draw(self.img)
        self.font = _font()
        self.regions: list[dict] = []

    def box_text(self, kind: str, xy: tuple[int, int], text: str, frame: bool = True) -> str:
        x, y = xy
        _, _, r, b = self.d.textbbox((x + 8, y + 6), text, font=self.font)
        bbox = [x, y, r + 8, b + 6]
        if frame:
            self.d.rectangle(bbox, outline=0, width=2)
            if kind == "fcf":  # vertical separators like a real frame
                cx = x + 8
                for part in text.split("|")[:-1]:
                    cx += self.d.textlength(part + "|", font=self.font)
                    self.d.line([cx - 4, y, cx - 4, bbox[3]], fill=0, width=1)
        self.d.text((x + 8, y + 6), text, fill=0, font=self.font)
        rid = f"{kind}-{len(self.regions)}"
        self.regions.append({"id": rid, "page": 0, "kind": kind, "bbox": bbox, "text": text})
        return rid


def make_drawing(name: str, rng: random.Random, defects: list[str]) -> tuple[Image.Image, dict]:
    s = _Sheet(name)
    d = s.d
    d.rectangle([20, 20, W - 20, H - 20], outline=0, width=3)
    # part outline with two holes
    px, py, pw, ph = 120, 200, rng.randint(420, 560), rng.randint(260, 360)
    d.rectangle([px, py, px + pw, py + ph], outline=0, width=3)
    for hx in (px + pw // 3, px + 2 * pw // 3):
        rr = rng.randint(18, 30)
        d.ellipse([hx - rr, py + ph // 2 - rr, hx + rr, py + ph // 2 + rr], outline=0, width=2)

    truth: list[dict] = []
    datums = ["A", "B"] + (["C"] if rng.random() < 0.5 else [])
    for i, letter in enumerate(datums):
        s.box_text("datum", (px + i * 160, py + ph + 40), f"DATUM {letter}")

    # feature control frames
    fcf_y = 120
    n_fcf = rng.randint(3, 5)
    fcfs = []
    for _ in range(n_fcf):
        char = rng.choice(["POS", "PERP", "PARA", "FLAT", "PROF"])
        tol = rng.choice([0.02, 0.05, 0.1, 0.2, 0.25])
        refs = [] if char == "FLAT" else rng.sample(datums, k=rng.randint(1, min(2, len(datums))))
        fcfs.append([char, tol, refs])

    if "missing_datum_ref" in defects:
        fcfs[0] = ["POS", 0.1, ["A", "D"]]
    if "form_with_datum" in defects:
        fcfs[1] = ["FLAT", 0.05, ["A"]]
    if "location_without_datum" in defects:
        fcfs[2] = ["POS", 0.2, []]
    if "zero_tolerance" in defects:
        fcfs[-1] = ["PERP", 0.0, ["A"]]

    fcf_ids = []
    for j, (char, tol, refs) in enumerate(fcfs):
        text = "|".join([char, f"{tol:.2f}", *refs])
        fcf_ids.append(s.box_text("fcf", (px + pw + 60, fcf_y + j * 56), text))

    # dimensions
    dim_ids = []
    n_dim = rng.randint(2, 4)
    for k in range(n_dim):
        nom = round(rng.uniform(4, 120), 2)
        dev = rng.choice([0.01, 0.02, 0.05, 0.1])
        prefix = "DIA " if rng.random() < 0.4 else ""
        up, lo = f"+{dev:.2f}", f"-{dev:.2f}"
        if "inverted_band" in defects and k == 0:
            up, lo = lo, up
        dim_ids.append(
            s.box_text(
                "dimension",
                (px + 20 + k * 150, py - 70 - (k % 2) * 40),
                f"{prefix}{nom:.2f} {up}/{lo}",
                frame=False,
            )
        )

    # BOM
    bx, by = W - 470, 40
    n_bom = rng.randint(2, 4)
    items = list(range(1, n_bom + 1))
    if "duplicate_item" in defects:
        items[-1] = items[0]
    bom_ids = []
    for r, item in enumerate(items):
        qty = rng.randint(1, 8)
        if "zero_qty" in defects and r == 0:
            qty = 0
        pn = f"PRT-{rng.randint(100, 999)}"
        bom_ids.append(s.box_text("bom_row", (bx, by + 600 + r * 44), f"{item} | {pn} | QTY {qty}"))

    # title block
    pn = f"SYN-{rng.randint(1000, 9999)}"
    rev = rng.choice("ABCDE")
    title = f"PN: {pn}" if "missing_revision" in defects else f"PN: {pn} REV: {rev}"
    title_id = s.box_text("title_block", (W - 470, H - 110), title)

    where = {
        "missing_datum_ref": [fcf_ids[0]],
        "form_with_datum": [fcf_ids[1]],
        "location_without_datum": [fcf_ids[2]],
        "zero_tolerance": [fcf_ids[-1]],
        "inverted_band": [dim_ids[0]],
        "missing_revision": [title_id],
        "zero_qty": [bom_ids[0]],
        "duplicate_item": [bom_ids[0], bom_ids[-1]],
    }
    for name_ in defects:
        truth.append({"defect": name_, "rule_id": DEFECT_RULE[name_], "region_ids": where[name_]})

    label = {"file": f"{name}.png", "synthetic": True, "regions": s.regions, "defects": truth}
    return s.img, label


def generate_set(out: Path, n: int = 12, seed: int = 7) -> list[Path]:
    rng = random.Random(seed)
    (out / "images").mkdir(parents=True, exist_ok=True)
    (out / "labels").mkdir(parents=True, exist_ok=True)
    paths = []
    for i in range(n):
        name = f"syn-{i:03d}"
        # about a third of drawings are clean, the rest carry one or two defects
        k = 0 if i % 3 == 0 else rng.choice([1, 1, 2])
        defects = rng.sample(DEFECTS, k=k)
        if "location_without_datum" in defects and "form_with_datum" in defects:
            defects.remove("form_with_datum")
        img, label = make_drawing(name, rng, defects)
        meta = PngInfo()
        meta.add_text("drw:annotations", json.dumps(label["regions"]))
        meta.add_text("drw:synthetic", "true")
        p = out / "images" / f"{name}.png"
        img.save(p, pnginfo=meta, optimize=True)
        (out / "labels" / f"{name}.json").write_text(json.dumps(label, indent=2))
        paths.append(p)
    return paths
