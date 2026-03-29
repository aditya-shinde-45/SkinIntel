"""
In-memory sliding-window rate limiter.
"""
import time
from collections import defaultdict, deque

from flask import request

from app.response import error_response


class RateLimiter:
    def __init__(self, requests_per_minute: int = 30):
        self.limit = requests_per_minute
        self._windows: dict = defaultdict(deque)

    def check(self):
        """Call as a before_request hook. Returns 429 response or None."""
        if not request.path.startswith("/api/v1/analyze"):
            return None

        ip = request.remote_addr or "unknown"
        now = time.time()
        window = self._windows[ip]

        # Evict entries older than 60 seconds
        while window and window[0] < now - 60:
            window.popleft()

        if len(window) >= self.limit:
            return error_response(
                "rate_limit_exceeded",
                f"Rate limit of {self.limit} requests/minute exceeded. Try again later.",
                status_code=429,
            )

        window.append(now)
        return None
