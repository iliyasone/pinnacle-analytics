from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from ps3838api.api import PinnacleClient

from app.core.config import settings
from app.core.security import verify_api_key
from app.db.models import APIKey
from app.schemas import (
    AccountInfoResponse,
    BetsRequest,
    BetsResponseModel,
    ClientBalanceRequest,
    ClientBalanceResponse,
)

router = APIRouter()


def get_pinnacle_client() -> PinnacleClient:
    return PinnacleClient(
        login=settings.PS3838_LOGIN,
        password=settings.PS3838_PASSWORD,
        api_base_url=settings.PS3838_API_BASE_URL,
    )


@router.post("/get_bets", response_model=BetsResponseModel)
async def get_bets(
    request: BetsRequest,
    client: PinnacleClient = Depends(get_pinnacle_client),
    api_key: APIKey = Depends(verify_api_key),
) -> BetsResponseModel:
    to_date = datetime.now(timezone.utc)
    from_date = to_date - timedelta(days=request.days)

    bets = client.get_bets(
        betlist="SETTLED",
        from_date=from_date,
        to_date=to_date,
    )

    return BetsResponseModel(**bets)


@router.post("/get_client_balance", response_model=ClientBalanceResponse)
async def get_client_balance(
    request: ClientBalanceRequest,
    client: PinnacleClient = Depends(get_pinnacle_client),
    api_key: APIKey = Depends(verify_api_key),
) -> ClientBalanceResponse:
    balance = client.get_client_balance()

    return ClientBalanceResponse(data=balance)


@router.get("/account_info", response_model=AccountInfoResponse)
async def get_account_info(
    api_key: APIKey = Depends(verify_api_key),
) -> AccountInfoResponse:
    return AccountInfoResponse(
        account_name=settings.PS3838_LOGIN,
        base_api_url=settings.PS3838_API_BASE_URL,
    )


@router.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "healthy"}
