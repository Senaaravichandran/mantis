"""Document OCR connector for PDF ingestion."""

from typing import Any
from .base import BaseConnector


class DocumentOCRConnector(BaseConnector):
    """Processes PDF documents using OCR for the RAG pipeline.

    Stub implementation for MVP. Full implementation will use
    Tesseract or PaddleOCR for PDF text extraction.
    """

    name = "document_ocr"
    poll_interval_seconds = 300  # Check for new documents every 5 minutes

    async def poll(self) -> list[dict[str, Any]]:
        # Stub: In production, watches MinIO bucket for new PDF uploads
        return []
