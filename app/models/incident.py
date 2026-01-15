from sqlalchemy import Column, String, DateTime, Text, Float, Enum as SQLEnum, JSON
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.sql import func
from .base import Base
import enum
import uuid


class IncidentStatus(str, enum.Enum):
    OPEN = "open"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    CLOSED = "closed"


class IncidentSeverity(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Incident(Base):
    """
    Represents a detected incident/failure in the system.
    """
    __tablename__ = "incidents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trace_id = Column(String, index=True, nullable=False)
    status = Column(SQLEnum(IncidentStatus), default=IncidentStatus.OPEN)
    severity = Column(SQLEnum(IncidentSeverity), default=IncidentSeverity.MEDIUM)
    detected_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    affected_services = Column(ARRAY(String), nullable=False)
    error_count = Column(Float, default=1)


class AnalysisResult(Base):
    """
    Stores AI-generated root cause analysis for incidents.
    """
    __tablename__ = "analysis_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    incident_id = Column(UUID(as_uuid=True), index=True, nullable=False)
    root_cause = Column(Text, nullable=False)
    confidence_score = Column(Float, nullable=False)
    evidence_signals = Column(ARRAY(UUID(as_uuid=True)), nullable=False)
    ai_explanation = Column(JSON, nullable=False)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
