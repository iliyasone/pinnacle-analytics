from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import APIKey


def verify_api_key(
    x_api_key: str = Header(..., description="API key for authentication"),
    db: Session = Depends(get_db),
) -> APIKey:
    db_key = db.query(APIKey).filter(APIKey.key == x_api_key, APIKey.is_active).first()
    if not db_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or inactive API key",
        )
    return db_key
