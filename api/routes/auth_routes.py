"""
DevOps Agent — Authentication Routes
"""

from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from typing import Optional
from config.settings import settings

router = APIRouter()


class LoginRequest(BaseModel):
    api_key: str


@router.post("/login")
async def login(request: LoginRequest):
    """Authenticate with API key."""
    if request.api_key == settings.api_key:
        return {"status": "authenticated", "token": "sim-token-abc123", "expires_in": 3600}
    raise HTTPException(status_code=401, detail="Invalid API key")


@router.get("/verify")
async def verify_token(authorization: Optional[str] = Header(None)):
    """Verify authentication token."""
    if authorization:
        return {"status": "valid", "user": "admin"}
    raise HTTPException(status_code=401, detail="No authorization header")
