"""PyJWT-backed implementation of the `TokenIssuer` port (HS256)."""

import uuid
from datetime import UTC, datetime, timedelta

import jwt

from athlos.modules.identity.application.ports import TokenIssuer
from athlos.modules.identity.domain.exceptions import InvalidTokenError
from athlos.modules.identity.domain.value_objects import UserId

_ALGORITHM = "HS256"

# 1 hour, no refresh token in this increment (see docs/DECISIONS.md).
# Lower this once refresh tokens / device management exist to shorten
# the exposure window of a leaked access token.
_TOKEN_TTL = timedelta(hours=1)


class PyJwtTokenIssuer(TokenIssuer):
    """Issues and verifies stateless JWTs signed with a single symmetric
    secret. No refresh tokens, rotation or revocation in this increment.
    """

    def __init__(self, secret: str) -> None:
        self._secret = secret

    def issue(self, user_id: UserId) -> str:
        now = datetime.now(UTC)
        payload = {
            "sub": str(user_id.value),
            "iat": now,
            "exp": now + _TOKEN_TTL,
        }
        return jwt.encode(payload, self._secret, algorithm=_ALGORITHM)

    def verify(self, token: str) -> UserId:
        try:
            payload = jwt.decode(token, self._secret, algorithms=[_ALGORITHM])
            return UserId(uuid.UUID(payload["sub"]))
        except (jwt.InvalidTokenError, KeyError, ValueError) as exc:
            raise InvalidTokenError() from exc
