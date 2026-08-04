"""
ETL Pipeline — EXTRACT Stage

Responsible for extracting raw text content from incoming documents.
Supports: PDF (via PyMuPDF), Images (via EasyOCR with multi-pass), Plain Text.

This is the first stage of the pipeline: raw bytes in → clean text out.
Note: Heavy OCR dependencies (easyocr, cv2, numpy) are lazily imported
so that basic text/PDF pipeline runs don't require ML vision libraries at import time.
"""

import fitz  # PyMuPDF
from collections import Counter
from typing import Optional, Any

from etl_pipeline.logger import get_logger

logger = get_logger(__name__)


# ─── Custom Exceptions ──────────────────────────────────────────────────────

class ExtractionError(Exception):
    """Raised when text extraction fails for any document type."""
    pass


# ─── EasyOCR Singleton (Lazy Loaded) ────────────────────────────────────────

_reader: Optional[Any] = None


def _get_easyocr_reader() -> Any:
    """Lazy-load EasyOCR reader (heavy model, load once on first image OCR request)."""
    global _reader
    if _reader is None:
        logger.info("Initializing EasyOCR reader (first-time load)...")
        try:
            import easyocr
        except ImportError:
            logger.error("EasyOCR package not installed.")
            raise ExtractionError("Image OCR failed: 'easyocr' module is not installed in the environment.")
        _reader = easyocr.Reader(["en"])
        logger.info("EasyOCR reader initialized successfully")
    return _reader


# ─── PDF Extraction ─────────────────────────────────────────────────────────

def _extract_from_pdf(file_bytes: bytes) -> str:
    """Extract text from PDF bytes using PyMuPDF."""
    text = ""
    with fitz.open(stream=file_bytes, filetype="pdf") as doc:
        page_count = len(doc)
        logger.debug(f"PDF has {page_count} page(s)")
        for i, page in enumerate(doc):
            page_text = page.get_text()
            text += page_text
            logger.debug(f"  Page {i + 1}: extracted {len(page_text)} chars")
    return text


# ─── Image OCR Extraction ───────────────────────────────────────────────────

def _multi_pass_ocr(img: Any) -> str:
    """
    Run EasyOCR on multiple preprocessed versions of the image
    and return the most consistent text (voting-based approach).

    This improves OCR accuracy for medical documents which may have
    varying contrast, fonts, and backgrounds.
    """
    try:
        import cv2
    except ImportError:
        raise ExtractionError("Image OCR failed: 'opencv-python' (cv2) is not installed in the environment.")

    reader = _get_easyocr_reader()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Create multiple image variants to improve OCR robustness
    variants = {
        "original": img,
        "grayscale": gray,
        "equalized": cv2.equalizeHist(gray),
        "adaptive_threshold": cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 31, 10,
        ),
        "otsu_threshold": cv2.threshold(
            gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )[1],
    }

    all_results = []
    for name, variant in variants.items():
        try:
            text = " ".join(reader.readtext(variant, detail=0))
            if text.strip():
                all_results.append(text)
                logger.debug(f"  OCR variant '{name}': {len(text)} chars extracted")
        except Exception as e:
            logger.warning(f"  OCR variant '{name}' failed: {e}")
            continue

    if not all_results:
        return ""

    # Vote on the best result across variants
    vote = Counter(all_results)
    best_text, count = vote.most_common(1)[0]
    logger.debug(f"  OCR voting: best result appeared {count}/{len(all_results)} times")
    return best_text


def _extract_from_image(file_bytes: bytes) -> str:
    """Extract text from image bytes using EasyOCR multi-pass."""
    try:
        import numpy as np
        import cv2
    except ImportError:
        raise ExtractionError("Image OCR failed: 'numpy' and 'opencv-python' are required for image decoding.")

    nparr = np.frombuffer(file_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img is None:
        raise ExtractionError("Could not decode image bytes — file may be corrupted")

    return _multi_pass_ocr(img)


# ─── Public API ──────────────────────────────────────────────────────────────

def extract_text(file_bytes: bytes, filename: str, mime: str) -> str:
    """
    EXTRACT stage entry point.

    Detects file type from MIME/filename, extracts raw text, and returns it.
    Raises ExtractionError if extraction fails or produces empty output.

    Args:
        file_bytes: Raw file content as bytes.
        filename:   Original filename (used for type detection fallback).
        mime:       MIME type of the uploaded file.

    Returns:
        Extracted text content as a string.

    Raises:
        ExtractionError: If text extraction fails or returns empty content.
    """
    file_size_kb = len(file_bytes) / 1024
    logger.info(f"EXTRACT | Starting extraction for '{filename}' "
                f"(type={mime}, size={file_size_kb:.1f} KB)")

    try:
        if "pdf" in mime or filename.lower().endswith(".pdf"):
            logger.info(f"EXTRACT | Detected PDF document")
            text = _extract_from_pdf(file_bytes)

        elif "image" in mime:
            logger.info(f"EXTRACT | Detected image, running OCR")
            text = _extract_from_image(file_bytes)

        else:
            logger.info(f"EXTRACT | Treating as plain text")
            text = file_bytes.decode("utf-8", errors="ignore")

    except ExtractionError:
        raise  # Re-raise our own exceptions as-is
    except Exception as e:
        logger.error(f"EXTRACT | Unexpected error during extraction: {e}")
        raise ExtractionError(f"Failed to extract text from '{filename}': {e}")

    if not text.strip():
        logger.error(f"EXTRACT | Extraction returned empty text for '{filename}'")
        raise ExtractionError(
            f"No text could be extracted from '{filename}'. "
            "The document may be empty or unreadable."
        )

    logger.info(f"EXTRACT | Completed — extracted {len(text)} characters")
    return text
