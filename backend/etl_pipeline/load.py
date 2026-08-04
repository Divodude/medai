"""
ETL Pipeline — LOAD Stage

Responsible for persisting processed data to storage systems:
1. Load text chunks into ChromaDB vector store (for RAG retrieval)
2. Load structured analysis results into SQLite (via SQLAlchemy ORM)

This is the final stage of the pipeline: processed data in → persistent storage.
"""

import os
from typing import List

from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from sqlalchemy.orm import Session as DBSession

from llm_provider import get_embeddings
from db import crud
from etl_pipeline.logger import get_logger

logger = get_logger(__name__)

# ─── Constants ───────────────────────────────────────────────────────────────

CHROMA_PERSIST_DIR = os.path.join(os.path.dirname(__file__), "..", "chroma_db")


# ─── Vector Store Loading ────────────────────────────────────────────────────

def load_to_vectorstore(chunks: List[str], session_id: str) -> int:
    """
    Load text chunks into ChromaDB vector store with session metadata.

    Each chunk is stored as a LangChain Document with session_id metadata,
    enabling filtered retrieval during RAG queries.

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
        # Build LangChain Document objects with session metadata
        documents = [
            Document(
                page_content=chunk,
                metadata={"session_id": session_id},
            )
            for chunk in chunks
        ]

        embeddings = get_embeddings()

        vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=embeddings,
            persist_directory=CHROMA_PERSIST_DIR,
        )

        logger.info(f"LOAD | Successfully loaded {len(documents)} documents "
                     f"to ChromaDB at '{CHROMA_PERSIST_DIR}'")
        return len(documents)

    except Exception as e:
        logger.error(f"LOAD | ChromaDB loading failed: {e}")
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
