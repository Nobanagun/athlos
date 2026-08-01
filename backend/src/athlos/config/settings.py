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


def get_cors_allowed_origins() -> list[str]:
    """Return the browser origins allowed to call this API (CORS).

    Empty by default, unlike `get_database_url()`/`get_jwt_secret()` -
    native iOS/Android traffic never goes through a browser and is
    unaffected by CORS, so requiring this variable would break the
    common case. Only opt-in origins (e.g. a local Expo Web build)
    should ever be listed here; never defaults to "*" - that would let
    any website call authenticated endpoints from a user's browser
    (see docs/DECISIONS.md).
    """
    raw = os.environ.get("CORS_ALLOWED_ORIGINS", "")
    return [origin.strip() for origin in raw.split(",") if origin.strip()]
