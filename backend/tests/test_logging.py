from __future__ import annotations

import logging

from api.logging import NoisyEndpointFilter


def _access_record(method: str, path: str) -> logging.LogRecord:
    return logging.LogRecord(
        name="uvicorn.access",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg='%s - "%s %s HTTP/%s" %s',
        args=("127.0.0.1:12345", method, path, "1.1", 200),
        exc_info=None,
    )


def test_noisy_endpoint_filter_suppresses_health_checks() -> None:
    assert not NoisyEndpointFilter().filter(_access_record("GET", "/health"))


def test_noisy_endpoint_filter_suppresses_run_polling() -> None:
    assert not NoisyEndpointFilter().filter(
        _access_record("GET", "/api/runs/00000000-0000-0000-0000-000000000001")
    )


def test_noisy_endpoint_filter_keeps_non_polling_requests() -> None:
    assert NoisyEndpointFilter().filter(_access_record("POST", "/api/analyze"))


def test_noisy_endpoint_filter_keeps_run_mutations() -> None:
    assert NoisyEndpointFilter().filter(
        _access_record("POST", "/api/runs/00000000-0000-0000-0000-000000000001")
    )
