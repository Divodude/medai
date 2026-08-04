"""
ETL Pipeline — Orchestrator

This module ties the Extract, Transform, and Load stages together into
a single `run_pipeline()` function. It manages:
- Pipeline status tracking via PipelineRun records
- Stage-by-stage execution with status updates
- Centralized error handling and failure logging

Usage:
    from etl_pipeline import run_pipeline

    result = run_pipeline(file_bytes, filename, mime, session_id, db)
"""

from datetime import datetime
from sqlalchemy.orm import Session as DBSession

from etl_pipeline.logger import get_logger
from etl_pipeline.extract import extract_text, ExtractionError
from etl_pipeline.transform import chunk_text, generate_knowledge
from etl_pipeline.load import load_to_vectorstore, load_to_database
from etl_pipeline.models import PipelineRun

logger = get_logger("etl_pipeline")


# ─── Pipeline Run Helpers ────────────────────────────────────────────────────

def _create_pipeline_run(db: DBSession, session_id: str, filename: str) -> PipelineRun:
    """Create a new PipelineRun record to track this execution."""
    run = PipelineRun(
        session_id=session_id,
        filename=filename,
        status="STARTED",
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    logger.info(f"PIPELINE | Created PipelineRun id={run.id} for '{filename}'")
    return run


def _update_run_status(db: DBSession, run: PipelineRun, status: str,
                       error_message: str = None, records_loaded: int = None):
    """Update the PipelineRun status (and optionally error/completion fields)."""
    run.status = status

    if error_message:
        run.error_message = error_message

    if records_loaded is not None:
        run.records_loaded = records_loaded

    if status in ("COMPLETED", "FAILED"):
        run.completed_at = datetime.utcnow()

    db.commit()
    logger.debug(f"PIPELINE | Run id={run.id} status -> {status}")


# ─── Main Pipeline Orchestrator ─────────────────────────────────────────────

def run_pipeline(
    file_bytes: bytes,
    filename: str,
    mime: str,
    session_id: str,
    db: DBSession,
) -> dict:
    """
    Execute the full ETL pipeline for a document upload.

    Pipeline stages:
        1. EXTRACT  — Pull raw text from the uploaded document
        2. TRANSFORM — Chunk text + generate structured knowledge via LLM
        3. LOAD     — Store vectors in ChromaDB + analysis results in SQLite

    Tracks pipeline execution via a PipelineRun record in the database.
    On failure at any stage, logs the error and marks the run as FAILED.

    Args:
        file_bytes: Raw bytes of the uploaded file.
        filename:   Original filename.
        mime:       MIME type of the file.
        session_id: Patient session identifier.
        db:         SQLAlchemy database session.

    Returns:
        Dictionary containing the analysis results for the API response.

    Raises:
        ExtractionError: If text extraction fails.
        RuntimeError:    If transform or load stages fail.
    """
    logger.info("=" * 60)
    logger.info(f"PIPELINE | Starting ETL pipeline for '{filename}' "
                f"(session={session_id})")
    logger.info("=" * 60)

    # Create audit trail record
    pipeline_run = _create_pipeline_run(db, session_id, filename)

    try:
        # ── Stage 1: EXTRACT ─────────────────────────────────────────
        _update_run_status(db, pipeline_run, "EXTRACTING")
        full_text = extract_text(file_bytes, filename, mime)

        # ── Stage 2: TRANSFORM ───────────────────────────────────────
        _update_run_status(db, pipeline_run, "TRANSFORMING")

        # 2a: Chunk text for vector store
        chunks = chunk_text(full_text)

        # 2b: Generate structured knowledge via LLM
        knowledge = generate_knowledge(full_text)
        result_dict = knowledge["result_dict"]

        # ── Stage 3: LOAD ────────────────────────────────────────────
        _update_run_status(db, pipeline_run, "LOADING")

        # 3a: Load chunks into ChromaDB
        num_loaded = load_to_vectorstore(chunks, session_id)

        # 3b: Save analysis to SQLite
        load_to_database(db, session_id, result_dict)

        # ── Mark pipeline as completed ───────────────────────────────
        _update_run_status(db, pipeline_run, "COMPLETED",
                           records_loaded=num_loaded)

        logger.info(f"PIPELINE | [OK] Pipeline completed successfully "
                    f"(run_id={pipeline_run.id}, chunks={num_loaded})")
        logger.info("=" * 60)

        return result_dict

    except (ExtractionError, RuntimeError) as e:
        # Known pipeline errors — log and mark as FAILED
        _update_run_status(db, pipeline_run, "FAILED", error_message=str(e))
        logger.error(f"PIPELINE | [FAILED] Pipeline FAILED at stage "
                     f"'{pipeline_run.status}': {e}")
        raise

    except Exception as e:
        # Unexpected errors — log and mark as FAILED
        _update_run_status(db, pipeline_run, "FAILED",
                           error_message=f"Unexpected error: {e}")
        logger.error(f"PIPELINE | [FAILED] Pipeline FAILED with unexpected error: {e}")
        raise RuntimeError(f"Pipeline failed unexpectedly: {e}")
