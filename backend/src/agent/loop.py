from __future__ import annotations

import asyncio
import json
import uuid
from datetime import UTC, datetime

import openai
import redis.asyncio as aioredis
from sqlalchemy.ext.asyncio import AsyncSession

from src.agent.registry import registry
from src.agent.tools import AgentContext
from src.config import settings
from src.db.models import Run, RunStatus
from src.db.session import engine

SYSTEM_PROMPT = (
    "You are an oil market intelligence analyst. You have access to tools "
    "to fetch market data, engineer features, run TabPFN classification, and explain "
    "predictions.\n\n"
    "Given a date range and analysis tasks, use the tools in this order:\n"
    "1. fetch_data — pull WTI (CL=F), DXY (DX-Y.NYB), XLE, SPY price series and INDPRO macro "
    "data\n"
    "2. engineer_features — featurize with windows [5, 20, 60] and lags [1, 5, 20]\n"
    "3. run_tabpfn with task='regime' — classify the current oil market regime\n"
    "4. run_tabpfn with task='direction' — predict WTI price direction over the next 20 trading "
    "days\n"
    "5. explain_prediction — pass the regime, direction, confidence, and 2-3 key feature "
    "names\n\n"
    "After calling explain_prediction, write a concise natural language summary (3-5 sentences) "
    "grounded in the actual confidence scores and feature values returned by the tools."
)

MAX_ITERATIONS = 10


async def _publish(redis_client: aioredis.Redis, channel: str, message: dict) -> None:  # type: ignore[type-arg]
    await redis_client.publish(channel, json.dumps(message, default=str))


async def run_agent_loop(
    run_id: uuid.UUID,
    date_range_start: str,
    date_range_end: str,
    tasks: list[str],
) -> None:
    """Drive the ReAct loop for one analysis run.

    Accepts primitive fields (not AnalyzeRequest) to avoid a circular import
    between src.agent.loop and api.routes.analyze.

    Creates its own DB session and Redis connection — must not reuse the
    HTTP request's session, which is closed once the response is sent.
    """
    redis_client: aioredis.Redis = aioredis.from_url(settings.redis_url)  # type: ignore[type-arg]
    channel = f"run:{run_id}"

    try:
        async with AsyncSession(engine) as session:
            run = await session.get(Run, run_id)
            if run is None:
                return
            run.status = RunStatus.RUNNING
            await session.commit()

        openai_client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
        context = AgentContext(
            date_range_start=date_range_start,
            date_range_end=date_range_end,
        )

        messages: list[dict] = [  # type: ignore[type-arg]
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Analyze {date_range_start} to {date_range_end}. Tasks: {tasks}",
            },
        ]

        last_text = ""
        total_input_tokens = 0
        total_output_tokens = 0
        for _ in range(MAX_ITERATIONS):
            response = await openai_client.chat.completions.create(
                model=settings.agent_model,
                tools=registry.schemas(),  # type: ignore[arg-type]
                messages=messages,  # type: ignore[arg-type]
            )
            if response.usage:
                total_input_tokens += response.usage.prompt_tokens
                total_output_tokens += response.usage.completion_tokens
            choice = response.choices[0]

            if choice.message.content:
                last_text = choice.message.content
                await _publish(redis_client, channel, {"type": "thought", "content": last_text})

            if choice.finish_reason == "tool_calls" and choice.message.tool_calls:
                assistant_msg: dict = {  # type: ignore[type-arg]
                    "role": "assistant",
                    "content": choice.message.content,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,  # type: ignore[union-attr]
                                "arguments": tc.function.arguments,  # type: ignore[union-attr]
                            },
                        }
                        for tc in choice.message.tool_calls
                    ],
                }
                messages.append(assistant_msg)

                for tc in choice.message.tool_calls:
                    name = tc.function.name  # type: ignore[union-attr]
                    arguments = json.loads(tc.function.arguments)  # type: ignore[union-attr]
                    await _publish(
                        redis_client,
                        channel,
                        {"type": "tool_call", "tool": name, "input": arguments},
                    )
                    result = await asyncio.to_thread(registry.dispatch, name, arguments, context)
                    await _publish(
                        redis_client,
                        channel,
                        {"type": "tool_result", "tool": name, "output": result},
                    )
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tc.id,
                            "content": json.dumps(result, default=str),
                        }
                    )
            else:
                break
        else:
            raise RuntimeError(f"Agent loop exceeded max iterations ({MAX_ITERATIONS})")

        estimated_cost = (
            total_input_tokens / 1000 * settings.agent_model_input_cost_per_1k
            + total_output_tokens / 1000 * settings.agent_model_output_cost_per_1k
        )
        usage = {
            "input_tokens": total_input_tokens,
            "output_tokens": total_output_tokens,
            "estimated_cost_usd": round(estimated_cost, 6),
        }

        await _publish(
            redis_client,
            channel,
            {"type": "done", "summary": last_text, "usage": usage},
        )

        async with AsyncSession(engine) as session:
            run = await session.get(Run, run_id)
            if run is not None:
                run.status = RunStatus.COMPLETED
                run.completed_at = datetime.now(UTC).replace(tzinfo=None)
                run.result = {
                    "regime": context.regime_result,
                    "direction": context.direction_result,
                    "summary": last_text,
                    "usage": usage,
                }
                await session.commit()

    except Exception as exc:
        await _publish(redis_client, channel, {"type": "error", "message": str(exc)})
        async with AsyncSession(engine) as session:
            run = await session.get(Run, run_id)
            if run is not None:
                run.status = RunStatus.FAILED
                run.error = str(exc)
                await session.commit()

    finally:
        await redis_client.aclose()  # type: ignore[attr-defined]
