"""
ETL Pipeline — LOAD Stage

Responsible for persisting processed data to storage systems:
1. Load text chunks into ChromaDB vector store (for RAG retrieval)
2. Load structured analysis results into SQLite (via SQLAlchemy ORM)

This is the final stage of the pipeline: processed data in → persistent storage.
"""

import os
import re
from typing import List

from sqlalchemy.orm import Session as DBSession

from llm_provider import get_embeddings
from db import crud
from etl_pipeline.logger import get_logger

# Prevent ONNX runtime threading issues on Windows (Errno 22) when running
# sentence-transformers inside uvicorn's async thread pool.
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

logger = get_logger(__name__)

# ─── Constants ───────────────────────────────────────────────────────────────

CHROMA_PERSIST_DIR = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "chroma_db")
)


def _safe_collection_name(session_id: str) -> str:
    """
    ChromaDB collection names must:
    - Be 3–63 characters long
    - Contain only alphanumerics, underscores, or hyphens
    - Not start/end with a hyphen or period
    Fix Windows [Errno 22] caused by invalid chars in ONNX temp paths.
    """
    safe = re.sub(r"[^a-zA-Z0-9_]", "_", str(session_id))
    if not safe or not safe[0].isalpha():
        safe = "s_" + safe
    return safe[:63]


# ─── Vector Store Loading ────────────────────────────────────────────────────

def load_to_vectorstore(chunks: List[str], session_id: str) -> int:
    """
    Load text chunks into ChromaDB vector store with session metadata.

    Uses the native chromadb Python client directly (not the langchain wrapper)
    to avoid [Errno 22] Invalid argument on Windows when running inside
    uvicorn's async thread pool (ONNX temp file conflict).

    Args:
        chunks:     List of text chunks to embed and store.
        session_id: Session identifier for metadata tagging.

    Returns:
        Number of documents loaded into the vector store.

    Raises:
        RuntimeError: If vector store loading fails.
    """
    logger.info(f"LOAD | Loading {len(chunks)} chunks into ChromaDB "
                f"(session={session_id})")

    try:
        embeddings_model = get_embeddings()
        collection_name = _safe_collection_name(session_id)

        logger.debug(f"LOAD | Using ChromaDB collection: '{collection_name}', "
                     f"persist_dir: '{CHROMA_PERSIST_DIR}'")

        # Embed all chunks in one batch call (avoids per-doc ONNX re-init)
        texts = chunks
        vectors = embeddings_model.embed_documents(texts)

        # Use native chromadb client — stable on Windows + chromadb >= 1.x
        import chromadb
        os.makedirs(CHROMA_PERSIST_DIR, exist_ok=True)
        client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
        collection = client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )

        # Build IDs and metadata for each chunk
        ids = [f"{collection_name}_{i}" for i in range(len(chunks))]
        metadatas = [{"session_id": session_id} for _ in chunks]

        collection.upsert(
            ids=ids,
            embeddings=vectors,
            documents=texts,
            metadatas=metadatas,
        )

        logger.info(f"LOAD | Successfully loaded {len(chunks)} documents "
                     f"to ChromaDB at '{CHROMA_PERSIST_DIR}'")
        return len(chunks)

    except Exception as e:
        import traceback
        logger.error(
            f"LOAD | ChromaDB loading failed: {e}\n"
            f"Full traceback:\n{traceback.format_exc()}"
        )
        raise RuntimeError(f"Vector store loading failed: {e}")


# ─── Database Loading ────────────────────────────────────────────────────────

def load_to_database(db: DBSession, session_id: str, result_dict: dict) -> int:
    """
    Persist the structured analysis result to SQLite via CRUD operations.

    Args:
        db:          SQLAlchemy database session.
        session_id:  Session identifier.
        result_dict: Flat dictionary containing analysis fields
                     (condition, severity, summary, key_findings, etc.)

    Returns:
        The ID of the created AnalysisResult record.

    Raises:
        RuntimeError: If database insertion fails.
    """
    logger.info(f"LOAD | Saving analysis result to database (session={session_id})")

    try:
        record = crud.save_analysis(db, session_id, result_dict)
        logger.info(f"LOAD | Analysis saved — record_id={record.id}, "
                     f"condition='{result_dict.get('condition', 'N/A')}'")
        return record.id

    except Exception as e:
        logger.error(f"LOAD | Database save failed: {e}")
        raise RuntimeError(f"Database loading failed: {e}")
