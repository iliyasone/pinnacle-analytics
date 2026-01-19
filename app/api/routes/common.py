from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from ps3838api.api import PinnacleClient
from ps3838api.models.bets import (
    BetsResponse,
    ManualBet,
    ParlayBetV2,
    SpecialBetV3,
    StraightBetV3,
    TeaserBet,
)

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
from app.schemas.responses import LeaguesResponse

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
    if request.from_date is not None and request.to_date is not None:
        from_date = request.from_date
        to_date = request.to_date
    else:
        to_date = datetime.now(timezone.utc)
        days = request.days or 1
        from_date = to_date - timedelta(days=days)

    # Split requests into 29-day chunks if necessary
    # API requires date range to be strictly less than 30 days
    max_span = timedelta(days=29, hours=23)
    current_date = from_date
    straight_bets: list[StraightBetV3] = []
    parlay_bets: list[ParlayBetV2] = []
    teaser_bets: list[TeaserBet] = []
    special_bets: list[SpecialBetV3] = []
    manual_bets: list[ManualBet] = []
    more_available = False

    while current_date < to_date:
        chunk_end = min(current_date + max_span, to_date)
        chunk_bets = client.get_bets(
            betlist="SETTLED",
            from_date=current_date,
            to_date=chunk_end,
        )

        more_available = more_available or chunk_bets.get("moreAvailable", False)
        straight_bets.extend(chunk_bets.get("straightBets", []))
        parlay_bets.extend(chunk_bets.get("parlayBets", []))
        teaser_bets.extend(chunk_bets.get("teaserBets", []))
        special_bets.extend(chunk_bets.get("specialBets", []))
        manual_bets.extend(chunk_bets.get("manualBets", []))

        current_date = chunk_end

    straight_bets = [bet for bet in straight_bets if bet["betStatus"] != "NOT_ACCEPTED"]

    total_records = (
        len(straight_bets) + len(parlay_bets) + len(teaser_bets) + len(special_bets) + len(manual_bets)
    )

    all_bets: BetsResponse = {
        "moreAvailable": more_available,
        "pageSize": total_records,
        "fromRecord": 0,
        "toRecord": total_records,
        "straightBets": straight_bets,
        "parlayBets": parlay_bets,
        "teaserBets": teaser_bets,
        "specialBets": special_bets,
        "manualBets": manual_bets,
    }

    return BetsResponseModel(**all_bets)


@router.post("/get_leagues", response_model=LeaguesResponse)
async def get_leagues(
    client: PinnacleClient = Depends(get_pinnacle_client),
    api_key: APIKey = Depends(verify_api_key),
) -> LeaguesResponse:
    leagues = client.get_leagues()

    return LeaguesResponse(leagues=leagues)


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
