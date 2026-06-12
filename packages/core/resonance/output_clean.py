"""Strip markdown code fences from LLM output before saving or linting."""

from __future__ import annotations

import re

_OPEN_FENCE = re.compile(r"^```(?:python|py)?\s*\r?\n?", re.IGNORECASE)
_CLOSE_FENCE = re.compile(r"\r?\n?```\s*$")


def clean_llm_output(text: str) -> str:
    """Return executable source: remove optional markdown fences, keep plain code."""
    if not text or not text.strip():
        return text

    stripped = text.strip("\ufeff").strip()
    if stripped.startswith("# Error:"):
        return stripped

    body = _OPEN_FENCE.sub("", stripped, count=1)
    body = _CLOSE_FENCE.sub("", body)
    return body.strip() + "\n"
