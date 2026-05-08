from contextlib import asynccontextmanager
from time import perf_counter

import sentry_sdk
import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import Response

from api.logging import configure_logging, should_log_request
from api.routes import analyze, derivatives, history
from api.ws import stream_handler
from src.config import settings

configure_logging()

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


@app.middleware("http")
async def log_requests(request: Request, call_next) -> Response:  # type: ignore[no-untyped-def]
    start = perf_counter()
    response = await call_next(request)
    if should_log_request(request.method, request.url.path):
        duration_ms = round((perf_counter() - start) * 1000, 2)
        log.info(
            "http.request",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=duration_ms,
        )
    return response


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
