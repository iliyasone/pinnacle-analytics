import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.db.migration import run_migrations

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan handler - runs on startup and shutdown."""
    # Startup: Run database migrations
    logger.info("Application startup: Running database migrations...")
    run_migrations()
    logger.info("Database migrations completed")

    yield

    # Shutdown (if needed in the future)
    logger.info("Application shutdown")


app = FastAPI(
    title="Pinnacle Analytics API",
    description="API for accessing Pinnacle betting data",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
