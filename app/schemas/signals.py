from enum import Enum
from typing import Dict, Any, Optional
from pydantic import Field
from .common import BaseSignal


class SignalType(str, Enum):
    LOG = "log"
    TRACE = "trace"
    METRIC = "metric"


class LogSignalV1(BaseSignal):
    signal_type: SignalType = SignalType.LOG
    level: str
    message: str
    attributes: Dict[str, Any] = Field(default_factory=dict)


class TraceSpanV1(BaseSignal):
    signal_type: SignalType = SignalType.TRACE
    span_id: str
    parent_span_id: Optional[str]
    duration_ms: float
    status: str
    attributes: Dict[str, Any] = Field(default_factory=dict)


class MetricSampleV1(BaseSignal):
    signal_type: SignalType = SignalType.METRIC
    metric_name: str
    value: float
    unit: str
    attributes: Dict[str, Any] = Field(default_factory=dict)
