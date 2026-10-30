import io

import pytest
from PIL import Image

from drawing_review.config import Settings
from drawing_review.ingest import IngestError, load_document, sniff


def png(w=50, h=40) -> bytes:
    buf = io.BytesIO()
    Image.new("L", (w, h), 255).save(buf, format="PNG")
    return buf.getvalue()


def test_sniff_by_magic_bytes_not_name():
    assert sniff(png()) == "image/png"
    with pytest.raises(IngestError) as e:
        sniff(b"MZ\x90\x00 not a drawing")
    assert e.value.status == 415


def test_empty_and_too_large():
    s = Settings(max_upload_mb=0.001)
    with pytest.raises(IngestError, match="empty"):
        load_document(b"", s)
    with pytest.raises(IngestError) as e:
        load_document(png(400, 400) + b"\0" * 5000, s)
    assert e.value.status == 413


def test_pixel_limit():
    with pytest.raises(IngestError) as e:
        load_document(png(300, 300), Settings(max_pixels=10_000))
    assert e.value.code == "too_many_pixels"


def test_truncated_png_is_rejected():
    with pytest.raises(IngestError) as e:
        load_document(png()[:30], Settings())
    assert e.value.code == "corrupt_file"


def test_pdf_is_rendered(tmp_path):
    buf = io.BytesIO()
    Image.new("RGB", (200, 100), "white").save(buf, format="PDF")
    doc = load_document(buf.getvalue(), Settings(target_long_side=400))
    assert len(doc.pages) == 1 and max(doc.pages[0].size) == 400


def test_document_id_is_content_hash():
    a = load_document(png(), Settings())
    b = load_document(png(), Settings())
    assert a.document_id == b.document_id and len(a.document_id) == 64
