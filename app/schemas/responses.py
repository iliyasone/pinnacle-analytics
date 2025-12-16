from datetime import datetime

from ps3838api.models.bets import ManualBet, ParlayBetV2, SpecialBetV3, StraightBetV3, TeaserBet
from ps3838api.models.client import BalanceData, LeagueV3
from pydantic import BaseModel


class BetsResponseModel(BaseModel):
    moreAvailable: bool
    pageSize: int
    fromRecord: int
    toRecord: int
    straightBets: list[StraightBetV3] = []
    parlayBets: list[ParlayBetV2] = []
    teaserBets: list[TeaserBet] = []
    specialBets: list[SpecialBetV3] = []
    manualBets: list[ManualBet] = []


class ClientBalanceResponse(BaseModel):
    data: BalanceData


class LeaguesResponse(BaseModel):
    leagues: list[LeagueV3]


class AccountInfoResponse(BaseModel):
    account_name: str | None
    base_api_url: str | None


class BillingPeriodBetsResponse(BaseModel):
    billing_period_day: int
    period_start: datetime
    period_end: datetime
    bets: BetsResponseModel
