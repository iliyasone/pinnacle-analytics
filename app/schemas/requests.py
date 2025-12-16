from pydantic import BaseModel, Field


class BetsRequest(BaseModel):
    days: int = Field(default=1, ge=1, le=30, description="Number of past days to retrieve bets (max 30)")


class ClientBalanceRequest(BaseModel):
    pass
