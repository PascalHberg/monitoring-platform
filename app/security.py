import os
import secrets

from fastapi import Header, HTTPException, status


def require_api_key(api_key: str | None = Header(default=None, alias="X-API-Key")) -> None:
    """Reject API requests unless the configured shared key is supplied."""
    expected_key = os.getenv("API_TOKEN")
    if not expected_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "API_AUTH_NOT_CONFIGURED",
                "message": "API access is disabled until the API_TOKEN environment variable is configured.",
            },
        )

    if not api_key or not secrets.compare_digest(api_key, expected_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "INVALID_API_TOKEN", "message": "A valid X-API-Key header is required."},
            headers={"WWW-Authenticate": "ApiKey"},
        )
