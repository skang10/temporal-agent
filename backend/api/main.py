from contextlib import asynccontextmanager

import sentry_sdk
import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import analyze, derivatives, history
from api.ws import stream_handler
from src.config import settings

log = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.sentry_dsn:
        sentry_sdk.init(dsn=settings.sentry_dsn, environment=settings.environment)
    log.info("startup", environment=settings.environment)
    yield
    log.info("shutdown")


app = FastAPI(title="TemporalAgent API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze.router, prefix="/api")
app.include_router(derivatives.router, prefix="/api")
app.include_router(history.router, prefix="/api")
app.add_api_websocket_route("/ws/runs/{run_id}/stream", stream_handler)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
