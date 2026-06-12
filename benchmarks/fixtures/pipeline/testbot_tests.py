"""Pytest suite — mixed cohesion."""

from __future__ import annotations


def test_login_success() -> None:
    assert check_status(200)


def test_login_failure() -> None:
    assert check_status(401)


def check_status(code: int) -> bool:
  return code in (200, 401)
