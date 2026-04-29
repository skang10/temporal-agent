from enum import StrEnum

from pydantic import BaseModel


class RunStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class RunResult(BaseModel):
    run_id: str
    status: RunStatus
    result: dict | None = None
