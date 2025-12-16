from typing import Literal

from pydantic import BaseModel, Field


class BetsRequest(BaseModel):
    days: int = Field(default=1, ge=1, le=30, description="Number of past days to retrieve bets (max 30)")


type BillingPeriodSelector = Literal["CURRENT", "PREVIOUS"]


class ClientBalanceRequest(BaseModel):
    pass


class BillingPeriodBetsRequest(BaseModel):
    period: BillingPeriodSelector = Field(
        default="CURRENT",
        description="Select which billing period to retrieve bets for",
    )
