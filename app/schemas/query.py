from pydantic import BaseModel
from typing import List, Optional, Any
from datetime import datetime
from uuid import UUID
from .signals import SignalType

class SignalRead(BaseModel):
    id: UUID
    signal_type: SignalType
    trace_id: str
    service_name: str
    timestamp: datetime
    payload: Any

    class Config:
        from_attributes = True

class PaginatedSignalResponse(BaseModel):
    items: List[SignalRead]
    total: int
    limit: int
    offset: int
