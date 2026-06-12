"""FastAPI routes — zombie pattern (isolated handlers, low Phi)."""

from __future__ import annotations


def login_route() -> str:
    return "/auth/login"


def logout_route() -> str:
    return "/auth/logout"


def refresh_route() -> str:
    return "/auth/refresh"
