from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.core.db import get_session
from app.api.v1.endpoints.auth import require_current_user
from app.models.user import User
from app.schemas.user import UserCreate, UserRead
from app.services.security import hash_password

router = APIRouter()


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, session: Session = Depends(get_session)) -> UserRead:
    normalized_email = payload.email.strip().lower()
    existing = session.exec(select(User).where(User.email == normalized_email)).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists")

    user = User(
        email=normalized_email,
        hashed_password=hash_password(payload.password),
        is_active=True,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.get("", response_model=list[UserRead])
def list_users(
    _: User = Depends(require_current_user),
    session: Session = Depends(get_session),
) -> list[UserRead]:
    users = session.exec(select(User)).all()
    return list(users)


@router.get("/{user_id}", response_model=UserRead)
def get_user(
    user_id: str,
    _: User = Depends(require_current_user),
    session: Session = Depends(get_session),
) -> UserRead:
    user = session.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user
