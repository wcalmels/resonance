"""Minimal context extraction — reduces input tokens 60-80% vs sending full files."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

ContextMode = Literal["tests", "endpoint", "module", "bugfix", "full"]


@dataclass
class ContextComparison:
    mode: str
    full_tokens: int
    minimal_tokens: int
    saved_tokens: int
    saved_percent: int
    minimal_context: str


class ContextSelector:
    """Extract only what each bot needs from a source file."""

    @staticmethod
    def estimate_tokens(text: str) -> int:
        """Rough estimate: ~4 characters per token."""
        return max(0, (len(text) + 3) // 4)

    @staticmethod
    def for_tests(file_content: str) -> str:
        lines = file_content.splitlines()
        relevant = []
        for line in lines:
            stripped = line.strip()
            if (
                stripped.startswith("def ")
                or stripped.startswith("async def")
                or stripped.startswith("class ")
                or stripped.startswith("import ")
                or stripped.startswith("from ")
            ):
                relevant.append(line)
        return "\n".join(relevant)

    @staticmethod
    def for_endpoint(file_content: str) -> str:
        lines = file_content.splitlines()
        relevant: list[str] = []
        in_route = False

        for line in lines:
            stripped = line.strip()
            if stripped.startswith("import ") or stripped.startswith("from "):
                relevant.append(line)
            elif stripped.startswith("@app.") or stripped.startswith("@router."):
                in_route = True
                relevant.append(line)
            elif in_route and (
                stripped.startswith("def ") or stripped.startswith("async def")
            ):
                relevant.append(line)
                relevant.append("    ...")
                in_route = False

        return "\n".join(relevant)

    @staticmethod
    def for_bug_fix(file_content: str, error_line: int) -> str:
        lines = file_content.splitlines()
        start = max(0, error_line - 30)
        end = min(len(lines), error_line + 30)
        return "\n".join(lines[start:end])

    @staticmethod
    def for_module(file_content: str) -> str:
        if not file_content:
            return ""
        lines = file_content.splitlines()
        relevant = []
        for line in lines:
            stripped = line.strip()
            if (
                stripped.startswith("import ")
                or stripped.startswith("from ")
                or stripped.startswith("class ")
            ):
                relevant.append(line)
        return "\n".join(relevant)

    @staticmethod
    def extract(
        file_content: str,
        mode: ContextMode,
        error_line: int | None = None,
    ) -> str:
        if mode == "full":
            return file_content
        if mode == "tests":
            return ContextSelector.for_tests(file_content)
        if mode == "endpoint":
            return ContextSelector.for_endpoint(file_content)
        if mode == "module":
            return ContextSelector.for_module(file_content)
        if mode == "bugfix":
            if error_line is None:
                raise ValueError("bugfix mode requires error_line")
            return ContextSelector.for_bug_fix(file_content, error_line)
        raise ValueError(f"Unknown context mode: {mode}")

    @staticmethod
    def compare(file_content: str, mode: ContextMode) -> ContextComparison:
        minimal = ContextSelector.extract(file_content, mode)
        full_tokens = ContextSelector.estimate_tokens(file_content)
        minimal_tokens = ContextSelector.estimate_tokens(minimal)
        saved = max(0, full_tokens - minimal_tokens)
        pct = round((saved / full_tokens) * 100) if full_tokens else 0
        return ContextComparison(
            mode=mode,
            full_tokens=full_tokens,
            minimal_tokens=minimal_tokens,
            saved_tokens=saved,
            saved_percent=pct,
            minimal_context=minimal,
        )

    @staticmethod
    def default_mode_for_bot(bot_name: str) -> ContextMode:
        return {
            "TestBot": "tests",
            "APIBot": "endpoint",
            "DatabaseBot": "module",
            "CodeBot": "module",
        }.get(bot_name, "module")
