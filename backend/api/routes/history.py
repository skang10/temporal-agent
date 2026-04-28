from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["history"])


class HistoryItem(BaseModel):
    run_id: str
    created_at: str
    regime: str | None
    status: str


@router.get("/history", response_model=list[HistoryItem])
async def get_history() -> list[HistoryItem]:
    # TODO: fetch recent runs from database
    raise NotImplementedError
