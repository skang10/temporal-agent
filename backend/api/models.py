from typing import Any

from pydantic import BaseModel

from src.db.models import RunStatus


class RunResult(BaseModel):
    run_id: str
    status: RunStatus
    result: dict[str, Any] | None = None
    error: str | None = None
