from fastapi import Header, HTTPException, status

from app.core.config import settings


def require_api_version(
    x_api_version: str | None = Header(default=None, alias="X-API-Version"),
) -> None:
    if x_api_version != settings.api_current_version:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid API version. Use header {settings.api_version_header_name}: {settings.api_current_version}",
        )
