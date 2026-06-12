"""Resonance execution engine — parallel specialized bot calls."""

from __future__ import annotations

import asyncio
import os
import time
from dataclasses import dataclass
from pathlib import Path

from resonance.bots import BOTS, MODEL
from resonance.output_clean import clean_llm_output

try:
    from anthropic import Anthropic
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    Anthropic = None  # type: ignore[misc, assignment]
    load_dotenv = None  # type: ignore[misc, assignment]


@dataclass
class BotResult:
    bot_name: str
    task: str
    output: str
    success: bool
    elapsed: float
    filename: str = ""
    input_tokens: int = 0
    output_tokens: int = 0


@dataclass
class ProjectSpec:
    name: str
    description: str
    requirements: list[str]
    output_dir: str = "output"


def get_client() -> Anthropic:
    if Anthropic is None:
        raise RuntimeError("Run: pip install anthropic python-dotenv")
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("Set ANTHROPIC_API_KEY in your .env file or environment")
    return Anthropic(api_key=api_key)


def run_bot(
    bot_name: str,
    task: str,
    context: str = "",
    client: Anthropic | None = None,
) -> BotResult:
    """Run a single bot synchronously."""
    if client is None:
        client = get_client()

    bot = BOTS[bot_name]
    t0 = time.time()

    messages = []
    if context.strip():
        messages.append(
            {
                "role": "user",
                "content": (
                    f"Existing code context:\n```python\n{context}\n```\n\nTask: {task}"
                ),
            }
        )
    else:
        messages.append({"role": "user", "content": task})

    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=1500,
            system=bot["system"],
            messages=messages,
        )
        output = clean_llm_output(response.content[0].text)
        success = True
        input_tokens = response.usage.input_tokens
        output_tokens = response.usage.output_tokens
    except Exception as exc:
        output = f"# Error: {exc}"
        success = False
        input_tokens = 0
        output_tokens = 0

    return BotResult(
        bot_name=bot_name,
        task=task,
        output=output,
        success=success,
        elapsed=round(time.time() - t0, 2),
        filename=f"{bot_name.lower()}{bot['filename_suffix']}",
        input_tokens=input_tokens,
        output_tokens=output_tokens,
    )


async def run_bot_async(
    bot_name: str,
    task: str,
    context: str = "",
    client: Anthropic | None = None,
) -> BotResult:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, run_bot, bot_name, task, context, client)


async def run_parallel(
    tasks: dict[str, str],
    context: str = "",
    client: Anthropic | None = None,
) -> list[BotResult]:
    return await asyncio.gather(
        *[run_bot_async(name, task, context, client) for name, task in tasks.items()]
    )


def save_results(results: list[BotResult], output_dir: str) -> None:
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    for result in results:
        if result.filename:
            path = Path(output_dir) / result.filename
            path.write_text(result.output, encoding="utf-8")
            print(f"  -> {path}  ({result.elapsed}s)")


async def generate(spec: ProjectSpec, context: str = "") -> list[BotResult]:
    print(f"\nGenerating: {spec.name}")
    print(f"Description: {spec.description}\n")

    base = f"{spec.description}. Requirements: {', '.join(spec.requirements)}"
    tasks = {
        "DatabaseBot": f"Create SQLAlchemy models for: {base}",
        "APIBot": f"Create FastAPI endpoints for: {base}",
        "TestBot": f"Create pytest tests for: {base}",
        "CodeBot": f"Create helper utilities for: {base}",
    }

    t0 = time.time()
    results = await run_parallel(tasks, context=context)
    total = round(time.time() - t0, 2)

    save_results(results, spec.output_dir)

    succeeded = sum(1 for r in results if r.success)
    print(f"\nDone: {succeeded}/{len(results)} bots succeeded in {total}s")
    print(f"Files in: {spec.output_dir}/")

    return results
