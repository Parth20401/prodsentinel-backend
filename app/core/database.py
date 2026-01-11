from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from .config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

logger.info("Initializing database engine")

engine = create_async_engine(settings.DATABASE_URL, echo=False)

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def get_db():
    """
    Database session dependency for FastAPI.
    Yields a database session and ensures proper cleanup.
    """
    try:
        async with AsyncSessionLocal() as session:
            yield session
            
    except SQLAlchemyError as exc:
        logger.error(f"Database session error: {exc}", exc_info=True)
        raise

