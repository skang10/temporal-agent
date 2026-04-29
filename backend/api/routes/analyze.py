from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from api.models import RunResult

router = APIRouter(tags=["analyze"])


class AnalyzeRequest(BaseModel):
    date_range_start: str
    date_range_end: str
    tasks: list[str] = ["regime_classification", "price_direction", "equity_outperformance"]


class AnalyzeResponse(BaseModel):
    run_id: str


@router.post("/analyze", response_model=AnalyzeResponse)
async def trigger_analysis(request: AnalyzeRequest) -> AnalyzeResponse:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Analysis pipeline is not implemented yet.",
    )


@router.get("/runs/{run_id}", response_model=RunResult)
async def get_run(run_id: str) -> RunResult:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Run storage is not implemented yet.",
    )
