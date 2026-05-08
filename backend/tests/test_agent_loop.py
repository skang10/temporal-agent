from __future__ import annotations

import json
import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.agent.loop import build_system_prompt, run_agent_loop
from src.db.models import RunStatus


class _SessionContext:
    def __init__(self, run: MagicMock) -> None:
        self.session = AsyncMock()
        self.session.get.return_value = run

    async def __aenter__(self) -> AsyncMock:
        return self.session

    async def __aexit__(self, *args: object) -> None:
        return None


class _SessionFactory:
    def __init__(self, run: MagicMock) -> None:
        self.run = run
        self.contexts: list[_SessionContext] = []

    def __call__(self, *args: object, **kwargs: object) -> _SessionContext:
        context = _SessionContext(self.run)
        self.contexts.append(context)
        return context


def _tool_call_response(name: str = "explain_prediction") -> SimpleNamespace:
    return SimpleNamespace(
        usage=SimpleNamespace(prompt_tokens=100, completion_tokens=50),
        choices=[
            SimpleNamespace(
                finish_reason="tool_calls",
                message=SimpleNamespace(
                    content=None,
                    tool_calls=[
                        SimpleNamespace(
                            id="call-1",
                            function=SimpleNamespace(
                                name=name,
                                arguments=json.dumps(
                                    {
                                        "regime": "range_bound",
                                        "direction": "up",
                                        "confidence": 0.7,
                                        "key_features": ["CL=F_roc_20d"],
                                    }
                                ),
                            ),
                        )
                    ],
                ),
            )
        ],
    )


def test_quick_prompt_limits_shap_and_skips_backtest_by_default() -> None:
    prompt = build_system_prompt("quick", ["regime_classification"])

    assert "evaluate_features with top_n=5 and max_samples=5" in prompt
    assert "Do not call backtest in quick mode unless tasks explicitly include" in prompt


def test_quick_prompt_allows_limited_backtest_when_requested() -> None:
    prompt = build_system_prompt("quick", ["backtest"])

    assert "backtest with horizon=20, step=60, max_windows=3" in prompt


def test_full_prompt_runs_full_backtest() -> None:
    prompt = build_system_prompt("full", ["regime_classification"])

    assert "evaluate_features with top_n=10 and max_samples=50" in prompt
    assert "backtest with horizon=20, step=20, max_windows=null" in prompt


@pytest.mark.asyncio
async def test_run_agent_loop_marks_failed_when_openai_credentials_missing() -> None:
    run = MagicMock()
    sessions = _SessionFactory(run)
    redis_client = AsyncMock()

    with (
        patch("src.agent.loop.AsyncSession", sessions),
        patch("src.agent.loop.aioredis.from_url", return_value=redis_client),
        patch("src.agent.loop.openai.AsyncOpenAI", side_effect=RuntimeError("missing key")),
    ):
        await run_agent_loop(uuid.uuid4(), "2024-01-01", "2024-02-01", ["regime"])

    assert run.status == RunStatus.FAILED
    assert "missing key" in run.error
    redis_client.aclose.assert_awaited_once()


@pytest.mark.asyncio
async def test_run_agent_loop_marks_failed_when_max_iterations_exhausted() -> None:
    run = MagicMock()
    sessions = _SessionFactory(run)
    redis_client = AsyncMock()
    openai_client = MagicMock()
    openai_client.chat.completions.create = AsyncMock(return_value=_tool_call_response())

    with (
        patch("src.agent.loop.AsyncSession", sessions),
        patch("src.agent.loop.aioredis.from_url", return_value=redis_client),
        patch("src.agent.loop.openai.AsyncOpenAI", return_value=openai_client),
    ):
        await run_agent_loop(uuid.uuid4(), "2024-01-01", "2024-02-01", ["regime"])

    assert openai_client.chat.completions.create.await_count == 10
    assert run.status == RunStatus.FAILED
    assert "max iterations" in run.error.lower()
