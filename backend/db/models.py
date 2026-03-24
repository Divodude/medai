from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from backend.db.database import Base


class Session(Base):
    """Represents a patient session (one report upload)."""
    __tablename__ = "sessions"

    id = Column(String, primary_key=True, index=True)  # UUID from frontend
    created_at = Column(DateTime, default=datetime.utcnow)
    patient_name = Column(String, default="Patient")

    analyses = relationship("AnalysisResult", back_populates="session", cascade="all, delete-orphan")
    diet_logs = relationship("DietLog", back_populates="session", cascade="all, delete-orphan")
    exercise_logs = relationship("ExerciseLog", back_populates="session", cascade="all, delete-orphan")
    doctor_results = relationship("DoctorResult", back_populates="session", cascade="all, delete-orphan")


class AnalysisResult(Base):
    """Stores the AI analysis result for a report image."""
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, ForeignKey("sessions.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    condition = Column(String)
    severity = Column(String)        # LOW | MEDIUM | HIGH
    summary = Column(Text)
    key_findings = Column(Text)      # JSON list as string
    specialty = Column(String)       # Medical specialty for doctor search

    diet_plan = Column(Text)         # JSON
    exercise_plan = Column(Text)     # JSON
    home_remedies = Column(Text)     # JSON

    session = relationship("Session", back_populates="analyses")


class DietLog(Base):
    """Tracks which diet items user has logged."""
    __tablename__ = "diet_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, ForeignKey("sessions.id"), nullable=False)
    meal_name = Column(String)
    logged_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("Session", back_populates="diet_logs")


class ExerciseLog(Base):
    """Tracks exercise completion."""
    __tablename__ = "exercise_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, ForeignKey("sessions.id"), nullable=False)
    exercise_name = Column(String)
    completed = Column(Boolean, default=False)
    logged_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("Session", back_populates="exercise_logs")


class DoctorResult(Base):
    """Stores nearby doctors returned by the search tool."""
    __tablename__ = "doctor_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, ForeignKey("sessions.id"), nullable=False)
    name = Column(String)
    specialty = Column(String)
    address = Column(String)
    phone = Column(String)
    rating = Column(Float, nullable=True)
    maps_link = Column(String, nullable=True)

    session = relationship("Session", back_populates="doctor_results")
