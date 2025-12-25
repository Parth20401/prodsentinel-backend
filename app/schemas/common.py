from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


class BaseSignal(BaseModel):
    """
    Canonical fields shared by all signals.
    This guarantees correlation and ordering.
    """
    signal_id: UUID
    trace_id: str = Field(..., min_length=1)
    service_name: str
    timestamp: datetime

    class Config:
        extra = "forbid"
