from typing import Any

from ps3838api.models.bets import BetsResponse
from pydantic import BaseModel


class BetsResponseModel(BaseModel):
    data: BetsResponse


class ClientBalanceResponse(BaseModel):
    data: Any
