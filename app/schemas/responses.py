from typing import Any

from ps3838api.models.bets import ManualBet, ParlayBetV2, SpecialBetV3, StraightBetV3, TeaserBet
from pydantic import BaseModel


class BetsResponseModel(BaseModel):
    moreAvailable: bool
    pageSize: int
    fromRecord: int
    toRecord: int
    straightBets: list[StraightBetV3]
    parlayBets: list[ParlayBetV2] = []
    teaserBets: list[TeaserBet] = []
    specialBets: list[SpecialBetV3] = []
    manualBets: list[ManualBet] = []


class ClientBalanceResponse(BaseModel):
    data: Any


class AccountInfoResponse(BaseModel):
    account_name: str | None
    base_api_url: str | None
