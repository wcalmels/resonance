"""SQLAlchemy models — refined connected pattern."""

from __future__ import annotations

from typing import Any


def build_user_record(data: dict[str, Any]) -> dict[str, Any]:
    return validate_user(normalize_user(data))


def normalize_user(data: dict[str, Any]) -> dict[str, Any]:
    return {"email": data.get("email", ""), "name": data.get("name", "")}


def validate_user(data: dict[str, Any]) -> dict[str, Any]:
    if not data.get("email"):
        raise ValueError("email required")
    return data
