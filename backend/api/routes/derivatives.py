from fastapi import APIRouter
from pydantic import BaseModel
from typing import Literal

router = APIRouter(tags=["derivatives"])


class DerivativesPriceRequest(BaseModel):
    regime: str
    spot: float
    strike: float
    tenor_days: int
    option_type: Literal["call", "put"] = "call"
    style: Literal["european", "american"] = "european"
    n_paths: int = 10_000


class DerivativesPriceResponse(BaseModel):
    price: float
    delta: float
    gamma: float
    vega: float
    theta: float
    paths: list[list[float]]  # sampled subset for visualization


@router.post("/derivatives/price", response_model=DerivativesPriceResponse)
async def price_derivative(request: DerivativesPriceRequest) -> DerivativesPriceResponse:
    # TODO: route to GBM or Heston based on regime, run Monte Carlo
    raise NotImplementedError
