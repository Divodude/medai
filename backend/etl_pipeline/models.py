"""
ETL Pipeline — PipelineRun Model

Tracks every ETL pipeline execution with status, timestamps, and error details.
Provides an audit trail for pipeline runs — useful for monitoring and debugging.

Status flow: STARTED → EXTRACTING → TRANSFORMING → LOADING → COMPLETED
On failure at any stage: status → FAILED (with error_message populated)
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from db.database import Base


class PipelineRun(Base):
    """
    Audit log for each ETL pipeline execution.

    Each time a document is uploaded and processed, a PipelineRun record
    is created to track progress through the Extract → Transform → Load stages.
    """
    __tablename__ = "pipeline_runs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, ForeignKey("sessions.id"), nullable=False)
    filename = Column(String, nullable=False)
    status = Column(String, default="STARTED")
    # Status values: STARTED | EXTRACTING | TRANSFORMING | LOADING | COMPLETED | FAILED

    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    records_loaded = Column(Integer, default=0)  # number of chunks loaded to vector store

    # Relationship back to session
    session = relationship("Session", back_populates="pipeline_runs")

    def __repr__(self) -> str:
        return (f"<PipelineRun(id={self.id}, session={self.session_id}, "
                f"status={self.status}, file='{self.filename}')>")
