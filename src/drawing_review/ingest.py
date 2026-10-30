"""Stage 1: ingestion and file validation.

Rejects anything we cannot process safely *before* it reaches a model: wrong type,
too large, too many pages, decompression bombs. Type is decided from magic bytes,
never from the file name or the client's Content-Type.
"""

from __future__ import annotations

import hashlib
import io
from dataclasses import dataclass, field

from PIL import Image

from .config import Settings

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
JPEG_MAGIC = b"\xff\xd8\xff"
PDF_MAGIC = b"%PDF-"


class IngestError(ValueError):
    """Raised for inputs the service refuses. ``code`` maps to an HTTP status."""

    def __init__(self, code: str, detail: str, status: int = 422):
        super().__init__(detail)
        self.code = code
        self.detail = detail
        self.status = status


@dataclass
class Document:
    document_id: str
    media_type: str
    pages: list[Image.Image]
    # Metadata carried by the file itself (PNG text chunks). Only the stub backends read it.
    metadata: dict[str, str] = field(default_factory=dict)


def sniff(data: bytes) -> str:
    if data.startswith(PNG_MAGIC):
        return "image/png"
    if data.startswith(JPEG_MAGIC):
        return "image/jpeg"
    if data.startswith(PDF_MAGIC):
        return "application/pdf"
    raise IngestError("unsupported_type", "Only PDF, PNG and JPEG files are accepted.", 415)


def load_document(data: bytes, settings: Settings) -> Document:
    if not data:
        raise IngestError("empty_file", "The uploaded file is empty.")
    if len(data) > settings.max_upload_mb * 1024 * 1024:
        raise IngestError("too_large", f"File exceeds {settings.max_upload_mb:g} MB.", status=413)
    media_type = sniff(data)
    doc_id = hashlib.sha256(data).hexdigest()

    if media_type == "application/pdf":
        pages = _render_pdf(data, settings)
        metadata: dict[str, str] = {}
    else:
        img = _open_image(data, settings)
        metadata = {k: v for k, v in img.info.items() if isinstance(v, str)}
        pages = [img]
    return Document(document_id=doc_id, media_type=media_type, pages=pages, metadata=metadata)


def _open_image(data: bytes, settings: Settings) -> Image.Image:
    Image.MAX_IMAGE_PIXELS = settings.max_pixels
    try:
        img = Image.open(io.BytesIO(data))
        img.load()
    except Image.DecompressionBombError as exc:
        raise IngestError("too_many_pixels", "Image resolution is above the limit.", 413) from exc
    except Exception as exc:  # corrupt or truncated file
        raise IngestError("corrupt_file", "The image could not be decoded.") from exc
    if img.width * img.height > settings.max_pixels:
        raise IngestError("too_many_pixels", "Image resolution is above the limit.", 413)
    return img


def _render_pdf(data: bytes, settings: Settings) -> list[Image.Image]:
    import pypdfium2 as pdfium

    try:
        pdf = pdfium.PdfDocument(data)
    except Exception as exc:
        raise IngestError("corrupt_file", "The PDF could not be opened.") from exc
    try:
        if len(pdf) == 0:
            raise IngestError("empty_file", "The PDF has no pages.")
        if len(pdf) > settings.max_pages:
            raise IngestError(
                "too_many_pages", f"PDF has more than {settings.max_pages} pages.", 413
            )
        pages = []
        for page in pdf:
            w, h = page.get_size()
            scale = settings.target_long_side / max(w, h)
            pages.append(page.render(scale=scale).to_pil())
        return pages
    finally:
        pdf.close()
