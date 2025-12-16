from collections.abc import AsyncGenerator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings


def normalize_database_url(url: str, async_driver: bool = True) -> str:
    """Normalize database URL.

    Handles both postgres:// and postgresql:// prefixes.
    If async_driver is True, uses asyncpg driver.
    """
    if url.startswith("postgres://"):
        base_url = url.replace("postgres://", "postgresql://", 1)
    else:
        base_url = url

    if async_driver and "+asyncpg" not in base_url:
        return base_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return base_url


# Async engine and session for FastAPI
ASYNC_DATABASE_URL = normalize_database_url(settings.database_url, async_driver=True)
engine = create_async_engine(ASYNC_DATABASE_URL)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Sync engine and session for CLI tools (alembic, manage_api_keys, etc.)
SYNC_DATABASE_URL = normalize_database_url(settings.database_url, async_driver=False)
sync_engine = create_engine(SYNC_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
