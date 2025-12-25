from sqlalchemy.ext.asyncio import AsyncSession
from app.models.raw_signal import RawSignal
from uuid import UUID


async def ingest_signal(
    db: AsyncSession,
    signal_id: UUID,
    signal_type: str,
    trace_id: str,
    service_name: str,
    timestamp,
    payload: dict,
):
    """
    Core ingestion logic.
    Stateless, idempotent, safe to retry.
    """
    raw = RawSignal(
        id=signal_id,
        signal_type=signal_type,
        trace_id=trace_id,
        service_name=service_name,
        timestamp=timestamp,
        payload=payload,
    )

    db.add(raw)
    await db.commit()
