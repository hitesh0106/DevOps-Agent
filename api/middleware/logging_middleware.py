"""
DevOps Agent — Request Logging Middleware
"""

import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from config.logging_config import get_logger

logger = get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Logs all incoming HTTP requests with timing."""

    async def dispatch(self, request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        duration_ms = (time.time() - start) * 1000

        logger.info(
            "HTTP Request",
            method=request.method,
            path=request.url.path,
            status=response.status_code,
            duration_ms=round(duration_ms, 2),
        )

        response.headers["X-Process-Time"] = f"{duration_ms:.2f}ms"
        return response
