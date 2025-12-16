from fastapi import Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.models import APIKey


async def verify_api_key(
    x_api_key: str = Header(..., description="API key for authentication"),
    db: AsyncSession = Depends(get_db),
) -> APIKey:
    result = await db.execute(select(APIKey).where(APIKey.key == x_api_key, APIKey.is_active == True))  # noqa: E712
    db_key = result.scalar_one_or_none()
    if not db_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or inactive API key",
        )
    return db_key
