"""Password hashing for the seeded `users` table.

There's no login flow anymore (Power BI handles viewer auth + RLS directly),
but `users.password_hash` still exists as seed data, so seed_data.py needs
this to generate it.
"""

from __future__ import annotations

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    return pwd_context.verify(plain_password, password_hash)
