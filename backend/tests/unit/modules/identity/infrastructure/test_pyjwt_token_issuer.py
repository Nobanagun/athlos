"""Tests for the PyJWT-backed TokenIssuer adapter (HS256) - no database
involved.
"""

from datetime import UTC, datetime, timedelta

import jwt
import pytest

from athlos.modules.identity.domain.exceptions import InvalidTokenError
from athlos.modules.identity.domain.value_objects import UserId
from athlos.modules.identity.infrastructure.jwt_token_issuer import PyJwtTokenIssuer

_SECRET = "test-secret-well-over-32-bytes-long"


def test_issue_then_verify_roundtrips_to_the_same_user_id() -> None:
    issuer = PyJwtTokenIssuer(secret=_SECRET)
    user_id = UserId.generate()

    token = issuer.issue(user_id)

    assert issuer.verify(token) == user_id


def test_verify_rejects_a_token_signed_with_a_different_secret() -> None:
    user_id = UserId.generate()
    token = PyJwtTokenIssuer(secret="secret-a-well-over-32-bytes-long").issue(user_id)

    with pytest.raises(InvalidTokenError):
        PyJwtTokenIssuer(secret="secret-b-well-over-32-bytes-long").verify(token)


def test_verify_rejects_a_malformed_token() -> None:
    issuer = PyJwtTokenIssuer(secret=_SECRET)

    with pytest.raises(InvalidTokenError):
        issuer.verify("not-a-jwt")


def test_verify_rejects_an_expired_token() -> None:
    issuer = PyJwtTokenIssuer(secret=_SECRET)
    now = datetime.now(UTC)
    expired_token = jwt.encode(
        {"sub": "not-checked", "iat": now - timedelta(hours=2), "exp": now - timedelta(hours=1)},
        _SECRET,
        algorithm="HS256",
    )

    with pytest.raises(InvalidTokenError):
        issuer.verify(expired_token)


def test_verify_rejects_a_token_without_a_sub_claim() -> None:
    issuer = PyJwtTokenIssuer(secret=_SECRET)
    now = datetime.now(UTC)
    token_without_sub = jwt.encode(
        {"iat": now, "exp": now + timedelta(hours=1)}, _SECRET, algorithm="HS256"
    )

    with pytest.raises(InvalidTokenError):
        issuer.verify(token_without_sub)


def test_issued_token_expires_about_one_hour_from_now() -> None:
    """Black-box check on the real emitted token, not the adapter's
    private `_TOKEN_TTL` constant - decodes with the same secret used to
    issue it, same as a real verifier would.
    """
    issuer = PyJwtTokenIssuer(secret=_SECRET)

    token = issuer.issue(UserId.generate())
    payload = jwt.decode(token, _SECRET, algorithms=["HS256"])

    assert payload["exp"] - payload["iat"] == timedelta(hours=1).total_seconds()
