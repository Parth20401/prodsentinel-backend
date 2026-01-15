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
        
        # Trigger analysis for ERROR logs
        if signal_type == "log" and payload.get("level") in ["ERROR", "CRITICAL"]:
            try:
                _trigger_analysis(trace_id)
            except Exception as exc:
                # Don't fail ingestion if analysis trigger fails
                logger.error(f"Failed to trigger analysis for {trace_id}: {exc}")
        
    except SQLAlchemyError as exc:
        await db.rollback()
        logger.error(f"Database error during ingestion: {exc}", exc_info=True)
        raise
        
    except Exception as exc:
        await db.rollback()
        logger.error(f"Unexpected error during ingestion: {exc}", exc_info=True)
        raise




def _trigger_analysis(trace_id: str):
    """
    Trigger async analysis via Celery (Fire and Forget).
    
    This is called synchronously but queues the task asynchronously.
    Uses a countdown to debounce multiple errors from the same trace.
    Deduplicates using Redis to ensure only one analysis task per trace_id.
    """
    try:
        import redis
        from celery import Celery
        from app.core.config import settings
        
        # Redis-based deduplication
        # Use a new connection for safety (or could use a connection pool)
        r = redis.from_url(settings.REDIS_URL, decode_responses=True)
        key = f"analysis:triggered:{trace_id}"
        
        # Check if already triggered (set if Not Exists)
        # Expires in 300s (5 mins) to allow re-analysis later if needed
        if not r.set(key, "1", ex=300, nx=True):
            logger.debug(f"Analysis already queued for trace_id: {trace_id}, skipping duplicate trigger")
            return
        
        # Create minimal Celery client (just for sending tasks)
        celery_client = Celery(broker=settings.REDIS_URL)
        
        # Queue analysis with 60s delay (debounce window)
        celery_client.send_task(
            "analyze_trace",
            args=[trace_id],
            countdown=60
        )
        
        logger.info(f"Analysis queued for trace_id: {trace_id} (60s delay)")
        
    except Exception as exc:
        # If queuing fails, delete key so it can be retried
        try:
            r = redis.from_url(settings.REDIS_URL, decode_responses=True)
            r.delete(f"analysis:triggered:{trace_id}")
        except:
            pass
            
        logger.error(f"Failed to queue Celery task: {exc}", exc_info=True)
        raise

