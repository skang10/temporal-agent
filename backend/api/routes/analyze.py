from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["analyze"])


class AnalyzeRequest(BaseModel):
    date_range_start: str
    date_range_end: str
    tasks: list[str] = ["regime_classification", "price_direction", "equity_outperformance"]


class AnalyzeResponse(BaseModel):
    run_id: str


class RunResult(BaseModel):
    run_id: str
    status: str
    result: dict | None = None


@router.post("/analyze", response_model=AnalyzeResponse)
async def trigger_analysis(request: AnalyzeRequest) -> AnalyzeResponse:
    # TODO: enqueue agent job via ARQ, return run_id
    raise NotImplementedError


@router.get("/runs/{run_id}", response_model=RunResult)
async def get_run(run_id: str) -> RunResult:
    # TODO: fetch run from database
    raise NotImplementedError
