"""FastAPI routes — refined connected pattern."""

from __future__ import annotations

from typing import Any


def handle_auth_request(action: str, payload: dict[str, Any]) -> dict[str, Any]:
    return route_response(resolve_action(action), payload)


def resolve_action(action: str) -> str:
    return action if action in {"login", "logout", "refresh"} else "login"


def route_response(action: str, payload: dict[str, Any]) -> dict[str, Any]:
    return {"action": action, "ok": bool(payload)}
