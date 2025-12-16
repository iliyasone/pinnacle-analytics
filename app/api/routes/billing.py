from calendar import monthrange
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from ps3838api.api import PinnacleClient

from app.api.routes.common import get_pinnacle_client
from app.core.config import settings
from app.core.security import verify_api_key
from app.db.models import APIKey
from app.schemas import BetsResponseModel, BillingPeriodBetsRequest, BillingPeriodBetsResponse
from app.schemas.requests import BillingPeriodSelector

router = APIRouter()


def _normalize_billing_day(year: int, month: int, billing_day: int) -> datetime:
    days_in_month = monthrange(year, month)[1]
    return datetime(year=year, month=month, day=min(billing_day, days_in_month), tzinfo=timezone.utc)


def _get_current_period_start(now: datetime, billing_day: int) -> datetime:
    if now.day >= billing_day:
        return _normalize_billing_day(now.year, now.month, billing_day)

    previous_month = now.month - 1 or 12
    previous_year = now.year - 1 if now.month == 1 else now.year
    return _normalize_billing_day(previous_year, previous_month, billing_day)


def _get_billing_period_bounds(
    period: BillingPeriodSelector, billing_day: int, now: datetime
) -> tuple[datetime, datetime]:
    current_period_start = _get_current_period_start(now, billing_day)

    if period == "CURRENT":
        return current_period_start, now

    previous_month = current_period_start.month - 1 or 12
    previous_year = (
        current_period_start.year - 1 if current_period_start.month == 1 else current_period_start.year
    )
    previous_period_start = _normalize_billing_day(previous_year, previous_month, billing_day)
    return previous_period_start, current_period_start - timedelta(microseconds=1)


@router.post("/billing_period_bets", response_model=BillingPeriodBetsResponse)
async def get_billing_period_bets(
    request: BillingPeriodBetsRequest,
    client: PinnacleClient = Depends(get_pinnacle_client),
    api_key: APIKey = Depends(verify_api_key),
) -> BillingPeriodBetsResponse:
    now = datetime.now(timezone.utc)
    period_start, period_end = _get_billing_period_bounds(request.period, settings.billing_period_day, now)

    bets = client.get_bets(
        betlist="SETTLED",
        from_date=period_start,
        to_date=period_end,
    )
    merged_bets = BetsResponseModel(**bets)

    return BillingPeriodBetsResponse(
        billing_period_day=settings.billing_period_day,
        period_start=period_start,
        period_end=period_end,
        bets=merged_bets,
    )
