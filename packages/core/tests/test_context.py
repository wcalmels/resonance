from resonance.context import ContextSelector


SAMPLE = '''import os
from typing import Optional

class UserService:
  def __init__(self, db):
    self.db = db

  def get_user(self, user_id: int) -> Optional[dict]:
    row = self.db.execute("SELECT * FROM users WHERE id = ?", user_id)
    return dict(row) if row else None

def validate_email(email: str) -> bool:
  return "@" in email and "." in email.split("@")[-1]
'''


def test_for_tests_keeps_signatures_only():
    result = ContextSelector.for_tests(SAMPLE)
    assert "def get_user" in result
    assert "def validate_email" in result
    assert "row = self.db.execute" not in result


def test_compare_shows_savings():
    comparison = ContextSelector.compare(SAMPLE, "tests")
    assert comparison.full_tokens > comparison.minimal_tokens
    assert comparison.saved_percent >= 50


def test_for_endpoint_keeps_routes():
    api_file = '''from fastapi import APIRouter
router = APIRouter()

@router.get("/users")
async def list_users():
    return db.query(User).all()
'''
    result = ContextSelector.for_endpoint(api_file)
    assert "@router.get" in result
    assert "return db.query" not in result


def test_default_mode_for_bot():
    assert ContextSelector.default_mode_for_bot("TestBot") == "tests"
    assert ContextSelector.default_mode_for_bot("APIBot") == "endpoint"
