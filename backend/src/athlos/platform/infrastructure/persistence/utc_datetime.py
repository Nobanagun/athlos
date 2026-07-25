"""Shared kernel `TypeDecorator` for timezone-aware UTC datetimes.

Promoted from `identity/infrastructure/models.py` (Fase 3, incremento
5), where it was first written to fix a real bug: SQLite silently
discards `tzinfo` on a plain `DateTime` column, even with
`timezone=True` (verified empirically). Every module with timestamps
needs this, not just `identity` - same reasoning as promoting `UserId`
(see docs/DECISIONS.md).
"""

from datetime import UTC, datetime

from sqlalchemy import DateTime, TypeDecorator
from sqlalchemy.engine import Dialect


class UtcDateTimeType(TypeDecorator[datetime]):
    """Stores as UTC-naive, reattaches `tzinfo=UTC` on read - so a
    timestamp is always timezone-aware regardless of whether it came
    fresh from construction or was loaded back from the database.
    """

    impl = DateTime
    cache_ok = True

    def process_bind_param(self, value: datetime | None, dialect: Dialect) -> datetime | None:
        if value is None:
            return None
        return value.astimezone(UTC).replace(tzinfo=None)

    def process_result_value(self, value: datetime | None, dialect: Dialect) -> datetime | None:
        if value is None:
            return None
        return value.replace(tzinfo=UTC)
