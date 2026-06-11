#!/usr/bin/env python3
"""Usage examples — requires ANTHROPIC_API_KEY in .env"""

import asyncio

from resonance import ProjectSpec, generate, run_bot


async def example_single_bot():
    print("=== Single Bot ===")
    result = run_bot("CodeBot", "Write a Python function that validates email addresses")
    print(f"Success: {result.success}, Time: {result.elapsed}s")
    print(result.output[:200])


async def example_full_project():
    print("\n=== Full Project ===")
    spec = ProjectSpec(
        name="Todo API",
        description="Simple todo list REST API",
        requirements=[
            "Create, read, update, delete todos",
            "Each todo has title, done flag, created_at",
            "Filter by done status",
        ],
        output_dir="output/todo_api",
    )
    await generate(spec)


async def main():
    await example_single_bot()
    await example_full_project()


if __name__ == "__main__":
    asyncio.run(main())
