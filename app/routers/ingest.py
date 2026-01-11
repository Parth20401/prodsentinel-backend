from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.schemas.signals import LogSignalV1
from app.services.ingestion_service import ingest_signal
from app.core.database import get_db
from app.core.logging import get_logger
from app.schemas.signals import LogSignalV1, TraceSpanV1, MetricSampleV1
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/ingest", tags=["ingest"])
logger = get_logger(__name__)


@router.post("/logs", status_code=status.HTTP_202_ACCEPTED)
async def ingest_log(
    signal: LogSignalV1,
    db: AsyncSession = Depends(get_db),
):
    """
    Ingest a log signal into the raw signals store.
    
    Args:
        signal: Log signal data conforming to LogSignalV1 schema
        db: Database session
        
    Returns:
        Acceptance confirmation
    """
    
    logger.info(
        f"Received log signal: trace_id={signal.trace_id}, "
        f"service={signal.service_name}, level={signal.level}"
    )
    
    try:
        await ingest_signal(
            db=db,
            signal_id=signal.signal_id,
            signal_type=signal.signal_type.value,
            trace_id=signal.trace_id,
            service_name=signal.service_name,
            timestamp=signal.timestamp,
            payload=signal.model_dump(mode='json'),
        )
        
        logger.info(f"Log signal accepted: signal_id={signal.signal_id}")
        return {"status": "accepted"}
        
    except Exception as exc:
        logger.error(f"Failed to ingest log signal: {exc}", exc_info=True)
        raise


@router.post("/traces", status_code=status.HTTP_202_ACCEPTED)
async def ingest_trace(
    signal: TraceSpanV1,
    db: AsyncSession = Depends(get_db),
):
    """Ingest a trace span into the raw signals store."""
    logger.info(
        f"Received trace span: trace_id={signal.trace_id}, "
        f"service={signal.service_name}, span_id={signal.span_id}"
    )
    
    try:
        await ingest_signal(
            db=db,
            signal_id=signal.signal_id,
            signal_type=signal.signal_type.value,
            trace_id=signal.trace_id,
            service_name=signal.service_name,
            timestamp=signal.timestamp,
            payload=signal.model_dump(mode='json'),
        )
        
        logger.info(f"Trace span accepted: signal_id={signal.signal_id}")
        return {"status": "accepted"}
        
    except Exception as exc:
        logger.error(f"Failed to ingest trace span: {exc}", exc_info=True)
        raise


@router.post("/metrics", status_code=status.HTTP_202_ACCEPTED)
async def ingest_metric(
    signal: MetricSampleV1,
    db: AsyncSession = Depends(get_db),
):
    """Ingest a metric sample into the raw signals store."""
    logger.info(
        f"Received metric: trace_id={signal.trace_id}, "
        f"service={signal.service_name}, metric={signal.metric_name}"
    )
    
    try:
        await ingest_signal(
            db=db,
            signal_id=signal.signal_id,
            signal_type=signal.signal_type.value,
            trace_id=signal.trace_id,
            service_name=signal.service_name,
            timestamp=signal.timestamp,
            payload=signal.model_dump(mode='json'),
        )
        
        logger.info(f"Metric accepted: signal_id={signal.signal_id}")
        return {"status": "accepted"}
        
    except Exception as exc:
        logger.error(f"Failed to ingest metric: {exc}", exc_info=True)
        raise

@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """Health check endpoint."""
    try:
        # Test database connection
        await db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected",
            "service": "ingestion-api"
        }
    except Exception as exc:
        logger.error(f"Health check failed: {exc}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "database": "disconnected",
                "error": str(exc)
            }
        )

