from collections import defaultdict
from time import monotonic

from fastapi import Request

import configuration
from exceptions import TooManyRequestsError

_attempts: dict[str, list[float]] = defaultdict(list)


def _client_key(request: Request) -> str:
    if request.client and request.client.host:
        return request.client.host
    return "unknown"


def enforce_login_rate_limit(request: Request) -> None:
    """Limit login attempts per client IP within a sliding time window."""
    key = _client_key(request)
    now = monotonic()
    window = configuration.LOGIN_RATE_LIMIT_WINDOW_SECONDS
    max_attempts = configuration.LOGIN_RATE_LIMIT_MAX
    attempts = [timestamp for timestamp in _attempts[key] if now - timestamp < window]

    if len(attempts) >= max_attempts:
        raise TooManyRequestsError(
            "Too many login attempts. Please try again later.",
            data={"retry_after_seconds": window},
        )

    attempts.append(now)
    _attempts[key] = attempts


def reset_login_rate_limits() -> None:
    """Clear tracked login attempts (for tests)."""
    _attempts.clear()
