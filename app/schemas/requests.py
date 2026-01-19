from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, model_validator


class BetsRequest(BaseModel):
    days: int | None = Field(default=1, ge=1, description="Number of past days to retrieve bets")
    from_date: datetime | None = Field(
        default=None,
        description="Start of the period to retrieve bets (ISO 8601). Mutually exclusive with days.",
    )
    to_date: datetime | None = Field(
        default=None,
        description="End of the period to retrieve bets (exclusive, ISO 8601). Mutually exclusive with days.",
    )

    @model_validator(mode="after")
    def validate_date_range(self) -> "BetsRequest":
        has_from = self.from_date is not None
        has_to = self.to_date is not None
        days_set = "days" in self.model_fields_set

        if has_from or has_to:
            if not (has_from and has_to):
                raise ValueError("from_date and to_date must be provided together")
            if days_set:
                raise ValueError("Provide either days or from_date/to_date, not both")
            if self.from_date is None or self.to_date is None:
                raise ValueError("from_date and to_date must be provided together")
            if self.from_date >= self.to_date:
                raise ValueError("to_date must be greater than from_date")
        elif self.days is None:
            raise ValueError("days is required when from_date/to_date are not provided")
        return self


type BillingPeriodSelector = Literal["CURRENT", "PREVIOUS"]


class ClientBalanceRequest(BaseModel):
    pass


class BillingPeriodBetsRequest(BaseModel):
    period: BillingPeriodSelector = Field(
        default="CURRENT",
        description="Select which billing period to retrieve bets for (CURRENT or PREVIOUS)",
    )
    api_gained_access: datetime | None = Field(
        default=None,
        description="Timestamp when API access was gained. Used to determine billing period boundaries. "
        "If not provided, defaults to billing_period_day from settings.",
    )
