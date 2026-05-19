from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Annotated

import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from configuration import (
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
    JWT_ALGORITHM,
    JWT_SECRET_KEY,
)
from exceptions import ForbiddenError, UnauthorizedError

bearer_scheme = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class CurrentUser:
    subject: str
    roles: list[str]


def create_access_token(
    subject: str,
    roles: list[str] | None = None,
    expires_delta: timedelta | None = None,
) -> str:
    expire = datetime.now(UTC) + (
        expires_delta or timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload = {"sub": subject, "roles": roles or [], "exp": expire}
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def _decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except jwt.InvalidTokenError as exc:
        raise UnauthorizedError("Invalid or expired token") from exc


def _parse_roles(raw_roles: object) -> list[str]:
    if not isinstance(raw_roles, list):
        return []
    return [role for role in raw_roles if isinstance(role, str)]


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> CurrentUser:
    if credentials is None:
        raise UnauthorizedError("Not authenticated")

    payload = _decode_token(credentials.credentials)
    subject = payload.get("sub")
    if not isinstance(subject, str) or not subject:
        raise UnauthorizedError("Invalid token payload")

    return CurrentUser(subject=subject, roles=_parse_roles(payload.get("roles")))


async def get_current_subject(user: CurrentUser = Depends(get_current_user)) -> str:
    return user.subject


def require_roles(*roles: str) -> Callable:
    async def checker(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if not any(role in user.roles for role in roles):
            raise ForbiddenError("Insufficient permissions")
        return user

    return checker


RequireAdmin = Annotated[CurrentUser, Depends(require_roles("admin"))]
RequireUser = Annotated[CurrentUser, Depends(require_roles("user"))]
