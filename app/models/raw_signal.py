from sqlalchemy import (
    Column, String, DateTime, Enum, JSON
)
from sqlalchemy.dialects.postgresql import UUID
from .base import Base
import enum


class SignalTypeEnum(str, enum.Enum):
    log = "log"
    trace = "trace"
    metric = "metric"


class RawSignal(Base):
    """
    Immutable raw signal store.
    NEVER updated after insert.
    """
    __tablename__ = "raw_signals"

    id = Column(UUID(as_uuid=True), primary_key=True)
    signal_type = Column(Enum(SignalTypeEnum), index=True)
    trace_id = Column(String, index=True)
    service_name = Column(String, index=True)
    timestamp = Column(DateTime(timezone=True), index=True)
    payload = Column(JSON, nullable=False)
