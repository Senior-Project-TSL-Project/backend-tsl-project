"""
API Key Authentication Middleware
"""

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader
import os

# API Key Header
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


def get_api_key() -> str:
    """Get API key from environment"""
    return os.getenv("API_KEY", "")


async def verify_api_key(api_key: str = Security(api_key_header)) -> str:
    """
    Verify the API key from request header.
    Returns the API key if valid, raises HTTPException if invalid.
    """
    expected_key = get_api_key()
    
    # If no API key configured, allow all requests (dev mode)
    if not expected_key:
        return ""
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API Key. Please provide X-API-Key header."
        )
    
    if api_key != expected_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API Key."
        )
    
    return api_key
