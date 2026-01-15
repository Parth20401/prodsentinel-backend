from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
# from app.routers import ingest  # Moved to bottom with query router
from app.core.logging import setup_logging, get_logger
from app.core.config import settings

# Initialize logging
setup_logging(log_level=settings.LOG_LEVEL)
logger = get_logger(__name__)

app = FastAPI(title="ProdSentinel Ingestion API")


# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with proper logging."""
    logger.warning(
        f"Validation error on {request.method} {request.url.path}",
        extra={"errors": exc.errors(), "body": exc.body},
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors with proper logging."""
    logger.error(
        f"Unexpected error on {request.method} {request.url.path}: {str(exc)}",
        exc_info=True,
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )


# Lifecycle events
@app.on_event("startup")
async def startup_event():
    """Log application startup."""
    logger.info(
        f"Starting {settings.APP_NAME} in {settings.APP_ENV} environment",
        extra={"app_name": settings.APP_NAME, "environment": settings.APP_ENV},
    )


@app.on_event("shutdown")
async def shutdown_event():
    """Log application shutdown."""
    logger.info(f"Shutting down {settings.APP_NAME}")


from app.routers import ingest, query

app.include_router(ingest.router)
app.include_router(query.router)

