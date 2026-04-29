from fastapi import APIRouter, HTTPException, status
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
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Run history is not implemented yet.",
    )
