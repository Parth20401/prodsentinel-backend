from fastapi import FastAPI
from app.routers import ingest

app = FastAPI(title="ProdSentinel Ingestion API")

app.include_router(ingest.router)
