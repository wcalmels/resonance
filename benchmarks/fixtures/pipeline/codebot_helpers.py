"""Helper utilities — connected pipeline (higher Phi)."""

from __future__ import annotations

from typing import Any


def normalize_payload(data: dict[str, Any]) -> dict[str, Any]:
    return validate_fields(transform_keys(data))


def transform_keys(data: dict[str, Any]) -> dict[str, Any]:
    return {str(k).lower(): v for k, v in data.items()}


def validate_fields(data: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in data.items() if v is not None}
