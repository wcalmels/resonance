"""SQLAlchemy models — zombie pattern (isolated functions, low Phi)."""

from __future__ import annotations


def user_table_name() -> str:
    return "users"


def session_table_name() -> str:
    return "sessions"


def token_table_name() -> str:
    return "tokens"
