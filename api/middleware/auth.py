
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from config.settings import settings


class APIKeyMiddleware(BaseHTTPMiddleware):
    """Validates API key for protected endpoints."""

    EXEMPT_PATHS = {"/", "/health", "/docs", "/redoc", "/openapi.json", "/webhook/github", "/webhook/alertmanager", "/webhook/custom"}

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # Skip auth for exempt paths and static files
        if path in self.EXEMPT_PATHS or path.startswith(("/css/", "/js/", "/assets/")):
            return await call_next(request)

        # Check API key
        api_key = request.headers.get("X-API-Key") or request.query_params.get("api_key")
        if api_key != settings.api_key:
            # In dev/simulation mode, allow all requests
            if settings.debug or settings.simulation_mode:
                return await call_next(request)
            raise HTTPException(status_code=401, detail="Invalid or missing API key")

        return await call_next(request)
