from __future__ import annotations

import logging
import os

from api.logging import NoisyEndpointFilter, configure_logging, should_log_request


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


def test_should_log_request_skips_polling_and_health() -> None:
    assert not should_log_request("GET", "/health")
    assert not should_log_request("GET", "/api/runs/00000000-0000-0000-0000-000000000001")


def test_should_log_request_keeps_useful_requests() -> None:
    assert should_log_request("POST", "/api/analyze")
    assert should_log_request("GET", "/api/history")


def test_configure_logging_disables_progress_bars_by_default(monkeypatch) -> None:
    monkeypatch.delenv("TQDM_DISABLE", raising=False)
    monkeypatch.delenv("HF_HUB_DISABLE_PROGRESS_BARS", raising=False)

    configure_logging()

    assert "TQDM_DISABLE" in os.environ
    assert "HF_HUB_DISABLE_PROGRESS_BARS" in os.environ
