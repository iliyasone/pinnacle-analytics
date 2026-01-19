from calendar import monthrange
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from ps3838api.api import PinnacleClient

from app.api.routes.common import get_bets, get_pinnacle_client
from app.core.config import settings
from app.core.security import verify_api_key
from app.db.models import APIKey
from app.schemas import BetsRequest, BillingPeriodBetsRequest, BillingPeriodBetsResponse
from app.schemas.requests import BillingPeriodSelector

router = APIRouter()


def _normalize_billing_day(
    year: int, month: int, billing_day: int, billing_time: tuple[int, int, int]
) -> datetime:
    """Normalize a billing day to a specific month, accounting for months with fewer days."""
    days_in_month = monthrange(year, month)[1]
    day = min(billing_day, days_in_month)
    return datetime(
        year=year,
        month=month,
        day=day,
        hour=billing_time[0],
        minute=billing_time[1],
        second=billing_time[2],
        tzinfo=timezone.utc,
    )


def _get_current_period_start(
    now: datetime, billing_day: int, billing_time: tuple[int, int, int]
) -> datetime:
    """Get the start of the current billing period based on the billing day and time."""
    current_time = (now.hour, now.minute, now.second)

    if now.day > billing_day or (now.day == billing_day and current_time >= billing_time):
        return _normalize_billing_day(now.year, now.month, billing_day, billing_time)

    previous_month = now.month - 1 or 12
    previous_year = now.year - 1 if now.month == 1 else now.year
    return _normalize_billing_day(previous_year, previous_month, billing_day, billing_time)


def _get_billing_period_bounds(
    period: BillingPeriodSelector, billing_day: int, billing_time: tuple[int, int, int], now: datetime
) -> tuple[datetime, datetime]:
    """Get the start and end boundaries of a billing period."""
    current_period_start = _get_current_period_start(now, billing_day, billing_time)

    # Period end is always the start of the next month's billing period
    next_month = current_period_start.month + 1 if current_period_start.month < 12 else 1
    next_year = (
        current_period_start.year if current_period_start.month < 12 else current_period_start.year + 1
    )
    current_period_end = _normalize_billing_day(next_year, next_month, billing_day, billing_time)

    if period == "CURRENT":
        return current_period_start, current_period_end

    # For PREVIOUS, get the start and end of the previous month's period
    previous_month = current_period_start.month - 1 or 12
    previous_year = (
        current_period_start.year - 1 if current_period_start.month == 1 else current_period_start.year
    )
    previous_period_start = _normalize_billing_day(previous_year, previous_month, billing_day, billing_time)
    return previous_period_start, current_period_start - timedelta(microseconds=1)


@router.post("/billing_period_bets", response_model=BillingPeriodBetsResponse)
async def get_billing_period_bets(
    request: BillingPeriodBetsRequest,
    client: PinnacleClient = Depends(get_pinnacle_client),
    api_key: APIKey = Depends(verify_api_key),
) -> BillingPeriodBetsResponse:
    now = datetime.now(timezone.utc)

    # Use provided api_gained_access or fall back to settings.api_gained_access
    if request.api_gained_access:
        access_ts = request.api_gained_access
        billing_day = access_ts.day
        billing_time = (access_ts.hour, access_ts.minute, access_ts.second)
    else:
        # Fallback: use settings.api_gained_access
        access_ts = settings.api_gained_access
        billing_day = settings.api_gained_access.day
        billing_time = (
            settings.api_gained_access.hour,
            settings.api_gained_access.minute,
            settings.api_gained_access.second,
        )

    period_start, period_end = _get_billing_period_bounds(request.period, billing_day, billing_time, now)

    bets_request = BetsRequest(from_date=period_start, to_date=period_end)
    merged_bets = await get_bets(request=bets_request, client=client, api_key=api_key)

    return BillingPeriodBetsResponse(
        api_gained_access=access_ts,
        billing_period_day=billing_day,
        period_start=period_start,
        period_end=period_end,
        bets=merged_bets,
    )
