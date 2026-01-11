from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from app.models.raw_signal import RawSignal
from app.core.logging import get_logger
from uuid import UUID

logger = get_logger(__name__)


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
    
    Args:
        db: Database session
        signal_id: Unique signal identifier
        signal_type: Type of signal (log, trace, metric)
        trace_id: Correlation ID for distributed tracing
        service_name: Name of the service emitting the signal
        timestamp: Signal timestamp
        payload: Full signal payload as dict
    """
    logger.debug(f"Processing {signal_type} signal: {signal_id}")
    
    try:
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
        logger.info(f"Signal stored: {signal_type} from {service_name}")
        
    except SQLAlchemyError as exc:
        await db.rollback()
        logger.error(f"Database error during ingestion: {exc}", exc_info=True)
        raise
        
    except Exception as exc:
        await db.rollback()
        logger.error(f"Unexpected error during ingestion: {exc}", exc_info=True)
        raise

