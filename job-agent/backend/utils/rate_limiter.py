import asyncio
import time
from functools import wraps
from typing import Callable


class RateLimiter:
    """Simple in-memory rate limiter using a token bucket algorithm.

    Args:
        max_calls: Maximum number of calls allowed per period.
        period: Time period in seconds.
    """

    def __init__(self, max_calls: int = 10, period: float = 60.0):
        self.max_calls = max_calls
        self.period = period
        self.calls: list = []

    def _clean_old_calls(self):
        """Remove calls that are older than the rate limit period."""
        now = time.monotonic()
        self.calls = [t for t in self.calls if now - t < self.period]

    def is_allowed(self) -> bool:
        """Check if a new call is allowed under the rate limit."""
        self._clean_old_calls()
        if len(self.calls) < self.max_calls:
            self.calls.append(time.monotonic())
            return True
        return False

    async def wait_if_needed(self):
        """Wait until a call is allowed under the rate limit."""
        while not self.is_allowed():
            await asyncio.sleep(0.5)


def rate_limited(max_calls: int = 10, period: float = 60.0):
    """Decorator to rate-limit async functions.

    Args:
        max_calls: Maximum number of calls per period.
        period: Time period in seconds.
    """
    limiter = RateLimiter(max_calls=max_calls, period=period)

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            await limiter.wait_if_needed()
            return await func(*args, **kwargs)

        return wrapper

    return decorator
