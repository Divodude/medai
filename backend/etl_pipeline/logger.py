"""
ETL Pipeline — Centralized Logging Configuration

Provides structured logging for the entire ETL pipeline with:
- Console output (StreamHandler) for development visibility
- Rotating file handler (logs/etl_pipeline.log) for production audit trails
- Consistent format: timestamp | level | module | message
"""

import os
import logging
from logging.handlers import RotatingFileHandler


# ─── Constants ───────────────────────────────────────────────────────────────
LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "logs")
LOG_FILE = os.path.join(LOG_DIR, "etl_pipeline.log")
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
MAX_LOG_SIZE = 5 * 1024 * 1024  # 5 MB per log file
BACKUP_COUNT = 3                # keep 3 rotated backups


def get_logger(module_name: str = "etl_pipeline") -> logging.Logger:
    """
    Returns a configured logger for the given module.

    Usage:
        from etl_pipeline.logger import get_logger
        logger = get_logger(__name__)
        logger.info("Pipeline started")

    Args:
        module_name: Name of the calling module (use __name__ for auto-detection).

    Returns:
        A configured logging.Logger instance.
    """
    logger = logging.getLogger(module_name)

    # Avoid adding duplicate handlers if get_logger is called multiple times
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    import sys
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    # ── Console Handler (INFO+) ──────────────────────────────────────────
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT))

    # ── File Handler (DEBUG+) with rotation ──────────────────────────────
    os.makedirs(LOG_DIR, exist_ok=True)
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=MAX_LOG_SIZE,
        backupCount=BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT))

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger
