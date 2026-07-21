"""Tests for the User aggregate.

Entity/AggregateRoot identity equality is already covered generically in
backend/tests/unit/platform/ (Fase 2) - not repeated here.
"""

from athlos.modules.identity.domain.events import UserRegistered
from athlos.modules.identity.domain.user import AccountStatus, User
from athlos.modules.identity.domain.value_objects import Email


def test_register_creates_an_active_user() -> None:
    user = User.register(Email("alice@example.com"))

    assert user.status is AccountStatus.ACTIVE
    assert user.email == Email("alice@example.com")


def test_register_records_exactly_one_user_registered_event() -> None:
    user = User.register(Email("alice@example.com"))

    events = user.domain_events
    assert len(events) == 1
    event = events[0]
    assert isinstance(event, UserRegistered)
    assert event.email == "alice@example.com"
    assert event.user_id == str(user.id.value)


def test_two_registrations_produce_different_user_ids() -> None:
    first = User.register(Email("alice@example.com"))
    second = User.register(Email("bob@example.com"))

    assert first.id != second.id
