from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.signals import LogSignalV1
from app.services.ingestion_service import ingest_signal
from app.core.database import get_db

router = APIRouter(prefix="/ingest", tags=["ingest"])


@router.post("/logs", status_code=status.HTTP_202_ACCEPTED)
async def ingest_log(
    signal: LogSignalV1,
    db: AsyncSession = Depends(get_db),
):
    await ingest_signal(
        db=db,
        signal_id=signal.signal_id,
        signal_type=signal.signal_type.value,
        trace_id=signal.trace_id,
        service_name=signal.service_name,
        timestamp=signal.timestamp,
        payload=signal.dict(),
    )

    return {"status": "accepted"}
