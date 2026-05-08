from datetime import UTC, datetime, timedelta

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.core.config import settings
from app.core.db import get_session
from app.models.user import User
from app.schemas.auth import (
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    MessageResponse,
    RefreshTokenRequest,
    ResetPasswordRequest,
    TokenRequest,
    TokenResponse,
)
from app.services.security import (
    create_access_token,
    create_refresh_token,
    create_reset_password_token,
    decode_token,
    hash_password,
    verify_password,
)

router = APIRouter()
_login_attempts: dict[str, dict[str, datetime | int]] = {}


@router.post("/token", response_model=TokenResponse)
def login_for_tokens(payload: TokenRequest, session: Session = Depends(get_session)) -> TokenResponse:
    key = payload.email.strip().lower()
    attempts = _login_attempts.get(key)
    if attempts:
        locked_until = attempts.get("locked_until")
        if isinstance(locked_until, datetime) and locked_until > datetime.now(UTC):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many failed attempts. Please wait and try again.",
            )

    user = session.exec(select(User).where(User.email == payload.email)).first()
    if user is None or not verify_password(payload.password, user.hashed_password):
        _record_failed_attempt(key)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    _login_attempts.pop(key, None)
    access_token = create_access_token(subject=user.id)
    refresh_token = create_refresh_token(subject=user.id)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=TokenResponse)
def refresh_tokens(payload: RefreshTokenRequest) -> TokenResponse:
    try:
        claims = decode_token(payload.refresh_token)
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token") from exc

    if claims.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    subject = claims.get("sub")
    if not subject:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    access_token = create_access_token(subject=subject)
    refresh_token = create_refresh_token(subject=subject)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/forgot-password", response_model=ForgotPasswordResponse)
def forgot_password(payload: ForgotPasswordRequest, session: Session = Depends(get_session)) -> ForgotPasswordResponse:
    # Primitive flow: do not reveal whether the email exists.
    user = session.exec(select(User).where(User.email == payload.email)).first()
    reset_token = None
    if user is not None and settings.env == "dev":
        reset_token = create_reset_password_token(subject=user.email)

    return ForgotPasswordResponse(
        message="If an account exists for that email, password reset instructions will be sent.",
        reset_token=reset_token,
    )


@router.post("/reset-password", response_model=MessageResponse)
def reset_password(payload: ResetPasswordRequest, session: Session = Depends(get_session)) -> MessageResponse:
    try:
        claims = decode_token(payload.token)
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid reset token") from exc

    if claims.get("type") != "reset":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid reset token")

    subject = claims.get("sub")
    if not subject:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid reset token")

    user = session.exec(select(User).where(User.email == subject)).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.hashed_password = hash_password(payload.new_password)
    session.add(user)
    session.commit()
    return MessageResponse(message="Password reset complete. You can now sign in.")


def _record_failed_attempt(key: str) -> None:
    now = datetime.now(UTC)
    attempts = _login_attempts.get(key, {"count": 0})
    count = int(attempts.get("count", 0)) + 1
    record: dict[str, datetime | int] = {"count": count}
    if count >= settings.login_max_attempts:
        record["locked_until"] = now + timedelta(minutes=settings.login_lockout_minutes)
        record["count"] = 0
    _login_attempts[key] = record
