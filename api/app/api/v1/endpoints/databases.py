from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlmodel import Session, select

from app.api.v1.endpoints.auth import require_current_user
from app.core.db import get_session
from app.models.database import Database
from app.models.user import User
from app.schemas.database import DatabaseCreate, DatabaseRead, DatabaseReplace, DatabaseUpdate

router = APIRouter()


@router.post("", response_model=DatabaseRead, status_code=status.HTTP_201_CREATED)
def create_database(
    payload: DatabaseCreate,
    _: User = Depends(require_current_user),
    session: Session = Depends(get_session),
) -> DatabaseRead:
    existing = session.exec(select(Database).where(Database.slug == payload.slug)).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Database slug already exists")
    db = Database(**payload.model_dump())
    session.add(db)
    session.commit()
    session.refresh(db)
    return db


@router.get("", response_model=list[DatabaseRead])
def list_databases(
    _: User = Depends(require_current_user),
    session: Session = Depends(get_session),
) -> list[DatabaseRead]:
    return list(session.exec(select(Database)).all())


@router.get("/{database_id}", response_model=DatabaseRead)
def get_database(
    database_id: str,
    _: User = Depends(require_current_user),
    session: Session = Depends(get_session),
) -> DatabaseRead:
    db = session.get(Database, database_id)
    if db is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Database not found")
    return db


@router.put("/{database_id}", response_model=DatabaseRead)
def replace_database(
    database_id: str,
    payload: DatabaseReplace,
    _: User = Depends(require_current_user),
    session: Session = Depends(get_session),
) -> DatabaseRead:
    db = session.get(Database, database_id)
    if db is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Database not found")
    if payload.slug != db.slug:
        existing = session.exec(select(Database).where(Database.slug == payload.slug)).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Database slug already exists")

    for key, value in payload.model_dump().items():
        setattr(db, key, value)
    db.updated_at = datetime.now(UTC)

    session.add(db)
    session.commit()
    session.refresh(db)
    return db


@router.patch("/{database_id}", response_model=DatabaseRead)
def update_database(
    database_id: str,
    payload: DatabaseUpdate,
    _: User = Depends(require_current_user),
    session: Session = Depends(get_session),
) -> DatabaseRead:
    db = session.get(Database, database_id)
    if db is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Database not found")

    updates = payload.model_dump(exclude_unset=True)
    if "slug" in updates and updates["slug"] != db.slug:
        existing = session.exec(select(Database).where(Database.slug == updates["slug"])).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Database slug already exists")
    for key, value in updates.items():
        setattr(db, key, value)
    db.updated_at = datetime.now(UTC)

    session.add(db)
    session.commit()
    session.refresh(db)
    return db


@router.delete("/{database_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
def delete_database(
    database_id: str,
    _: User = Depends(require_current_user),
    session: Session = Depends(get_session),
) -> Response:
    db = session.get(Database, database_id)
    if db is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Database not found")

    session.delete(db)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
