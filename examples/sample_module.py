"""Sample module for demonstrating token savings."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class User:
    id: int
    email: str
    active: bool = True


class UserRepository:
    def __init__(self, connection):
        self.connection = connection

    def find_by_email(self, email: str) -> Optional[User]:
        cursor = self.connection.execute(
            "SELECT id, email, active FROM users WHERE email = ?",
            (email,),
        )
        row = cursor.fetchone()
        if not row:
            return None
        return User(id=row[0], email=row[1], active=bool(row[2]))

    def create(self, email: str) -> User:
        if not validate_email(email):
            raise ValueError("invalid email")
        cursor = self.connection.execute(
            "INSERT INTO users (email, active) VALUES (?, 1) RETURNING id",
            (email,),
        )
        user_id = cursor.fetchone()[0]
        return User(id=user_id, email=email)


def validate_email(email: str) -> bool:
  pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
  return bool(re.match(pattern, email))
