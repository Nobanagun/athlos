"""Integration tests for SqlAlchemyUserRepository against a real engine."""

import pytest
from sqlalchemy import Engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from athlos.modules.identity.domain.user import AccountStatus, User
from athlos.modules.identity.domain.value_objects import Email, PasswordHash, UserId
from athlos.modules.identity.infrastructure.repository import SqlAlchemyUserRepository
from athlos.platform.infrastructure.outbox.models import OutboxMessage
from athlos.platform.infrastructure.unit_of_work import SqlAlchemyUnitOfWork

_PASSWORD_HASH = PasswordHash("$argon2id$fake-hash-for-tests")


def test_add_and_get_by_id_roundtrip_preserves_value_objects(session: Session) -> None:
    repo = SqlAlchemyUserRepository(session)
    user = User.register(Email("alice@example.com"), _PASSWORD_HASH)

    repo.add(user)
    session.commit()

    fetched = repo.get_by_id(user.id)

    assert fetched is not None
    assert isinstance(fetched.id, UserId)
    assert fetched.id == user.id
    assert isinstance(fetched.email, Email)
    assert fetched.email == Email("alice@example.com")
    assert fetched.password_hash == _PASSWORD_HASH
    assert fetched.status is AccountStatus.ACTIVE


def test_get_by_id_returns_none_when_not_found(session: Session) -> None:
    repo = SqlAlchemyUserRepository(session)

    assert repo.get_by_id(UserId.generate()) is None


def test_get_by_email_finds_normalized_match(session: Session) -> None:
    repo = SqlAlchemyUserRepository(session)
    user = User.register(Email("Alice@Example.com"), _PASSWORD_HASH)
    repo.add(user)
    session.commit()

    found = repo.get_by_email(Email("alice@example.com"))

    assert found is not None
    assert found.id == user.id


def test_get_by_email_returns_none_when_not_found(session: Session) -> None:
    repo = SqlAlchemyUserRepository(session)

    assert repo.get_by_email(Email("nobody@example.com")) is None


def test_duplicate_email_violates_unique_constraint(session: Session) -> None:
    repo = SqlAlchemyUserRepository(session)
    repo.add(User.register(Email("alice@example.com"), _PASSWORD_HASH))
    session.commit()

    repo.add(User.register(Email("alice@example.com"), _PASSWORD_HASH))
    with pytest.raises(IntegrityError):
        session.commit()


def test_integrity_error_rolls_back_transaction_completely(engine: Engine) -> None:
    """A real database-level failure (not the application-level check)
    must leave nothing behind - neither the user row nor its outbox
    event. Verified with a brand-new session, so nothing in the failed
    session's local state can mask a partial write.
    """
    factory = sessionmaker(bind=engine)

    with factory() as setup_session:
        setup_repo = SqlAlchemyUserRepository(setup_session)
        setup_uow = SqlAlchemyUnitOfWork(setup_session)
        setup_repo.add(User.register(Email("alice@example.com"), _PASSWORD_HASH))
        setup_uow.commit()

    # Bypass the application-level uniqueness check entirely (simulating
    # a race condition) so the failure happens inside commit() itself.
    with factory() as racing_session:
        repo = SqlAlchemyUserRepository(racing_session)
        uow = SqlAlchemyUnitOfWork(racing_session)
        second = User.register(Email("alice@example.com"), _PASSWORD_HASH)
        repo.add(second)

        with pytest.raises(IntegrityError):
            uow.commit()

    with factory() as verification_session:
        verify_repo = SqlAlchemyUserRepository(verification_session)
        assert verify_repo.get_by_id(second.id) is None

        outbox_rows = (
            verification_session.query(OutboxMessage).filter_by(event_type="UserRegistered").all()
        )
        assert len(outbox_rows) == 1


def test_fetched_user_domain_events_does_not_crash(engine: Engine) -> None:
    """Regression test: a `_MappedUser` reconstituted by SQLAlchemy from a
    row (not freshly constructed in Python) never goes through
    `AggregateRoot.__init__`, so `_domain_events` would not exist unless
    `AggregateRoot` treats a missing list as "no events yet" (see
    `platform/domain/entity.py`). Loaded in a brand-new session so this
    is a genuine load, not a reused in-memory instance.
    """
    factory = sessionmaker(bind=engine)

    with factory() as setup_session:
        setup_repo = SqlAlchemyUserRepository(setup_session)
        setup_uow = SqlAlchemyUnitOfWork(setup_session)
        setup_repo.add(User.register(Email("regression@example.com"), _PASSWORD_HASH))
        setup_uow.commit()

    with factory() as fresh_session:
        repo = SqlAlchemyUserRepository(fresh_session)
        fetched = repo.get_by_email(Email("regression@example.com"))

        assert fetched is not None
        assert fetched.domain_events == ()
