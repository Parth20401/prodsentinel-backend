from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from datetime import datetime
from app.core.database import get_db
from app.schemas.query import SignalRead, PaginatedSignalResponse
from app.services import query_service
from app.core.logging import get_logger

router = APIRouter(prefix="/query", tags=["query"])
logger = get_logger(__name__)

@router.get("/signals", response_model=PaginatedSignalResponse)
async def list_signals(
    trace_id: Optional[str] = Query(None),
    service_name: Optional[str] = Query(None),
    signal_type: Optional[str] = Query(None),
    start_time: Optional[datetime] = Query(None),
    end_time: Optional[datetime] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve raw signals with optional filtering and pagination.
    """
    logger.info(f"Querying signals: trace_id={trace_id}, service={service_name}")
    
    signals, total = await query_service.get_signals(
        db=db,
        trace_id=trace_id,
        service_name=service_name,
        signal_type=signal_type,
        start_time=start_time,
        end_time=end_time,
        limit=limit,
        offset=offset
    )
    
    return {
        "items": signals,
        "total": total,
        "limit": limit,
        "offset": offset
    }

@router.get("/traces/{trace_id}", response_model=List[SignalRead])
async def get_trace(
    trace_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve all signals correlated by a specific trace_id.
    """
    logger.info(f"Retrieving trace: {trace_id}")
    
    signals = await query_service.get_trace_signals(db, trace_id)
    
    if not signals:
        logger.warning(f"No signals found for trace_id: {trace_id}")
        # We return empty list instead of 404 as it's a valid query result
        return []
        
    return signals
