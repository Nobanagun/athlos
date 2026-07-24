"""Minimal application configuration.

No `pydantic-settings`: a single required variable does not justify a
new dependency (see docs/DECISIONS.md). Mirrors how `migrations/env.py`
already reads `DATABASE_URL` directly from `os.environ`.
"""

import os


def get_database_url() -> str:
    """Return the configured database URL, or raise if it is missing."""
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is not set - see backend/.env.example.")
    return database_url


def get_jwt_secret() -> str:
    """Return the configured JWT signing secret, or raise if it is
    missing. Symmetric (HS256) - the same value signs and verifies
    tokens in this increment (see docs/DECISIONS.md).
    """
    secret = os.environ.get("JWT_SECRET")
    if not secret:
        raise RuntimeError("JWT_SECRET is not set - see backend/.env.example.")
    return secret
