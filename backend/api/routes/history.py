from fastapi import APIRouter
from pydantic import BaseModel

from api.models import RunStatus

router = APIRouter(tags=["history"])


class HistoryItem(BaseModel):
    run_id: str
    created_at: str
    regime: str | None
    status: RunStatus


@router.get("/history", response_model=list[HistoryItem])
async def get_history() -> list[HistoryItem]:
    raise NotImplementedError
