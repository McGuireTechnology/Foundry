from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlmodel import Session, select

from app.api.v1.endpoints.auth import require_current_user
from app.core.db import get_session
from app.models.application import Application
from app.models.user import User
from app.schemas.application import ApplicationCreate, ApplicationRead, ApplicationReplace, ApplicationUpdate

router = APIRouter()


@router.post("", response_model=ApplicationRead, status_code=status.HTTP_201_CREATED)
def create_application(
    payload: ApplicationCreate,
    _: User = Depends(require_current_user),
    session: Session = Depends(get_session),
) -> ApplicationRead:
    existing = session.exec(select(Application).where(Application.slug == payload.slug)).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Application slug already exists")

    app = Application(**payload.model_dump())
    session.add(app)
    session.commit()
    session.refresh(app)
    return app


@router.get("", response_model=list[ApplicationRead])
def list_applications(
    _: User = Depends(require_current_user),
    session: Session = Depends(get_session),
) -> list[ApplicationRead]:
    return list(session.exec(select(Application)).all())


@router.get("/{application_id}", response_model=ApplicationRead)
def get_application(
    application_id: str,
    _: User = Depends(require_current_user),
    session: Session = Depends(get_session),
) -> ApplicationRead:
    app = session.get(Application, application_id)
    if app is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")
    return app


@router.put("/{application_id}", response_model=ApplicationRead)
def replace_application(
    application_id: str,
    payload: ApplicationReplace,
    _: User = Depends(require_current_user),
    session: Session = Depends(get_session),
) -> ApplicationRead:
    app = session.get(Application, application_id)
    if app is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")

    if payload.slug != app.slug:
        existing = session.exec(select(Application).where(Application.slug == payload.slug)).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Application slug already exists")

    for key, value in payload.model_dump().items():
        setattr(app, key, value)
    app.updated_at = datetime.now(UTC)

    session.add(app)
    session.commit()
    session.refresh(app)
    return app


@router.patch("/{application_id}", response_model=ApplicationRead)
def update_application(
    application_id: str,
    payload: ApplicationUpdate,
    _: User = Depends(require_current_user),
    session: Session = Depends(get_session),
) -> ApplicationRead:
    app = session.get(Application, application_id)
    if app is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")

    updates = payload.model_dump(exclude_unset=True)
    if "slug" in updates and updates["slug"] != app.slug:
        existing = session.exec(select(Application).where(Application.slug == updates["slug"])).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Application slug already exists")

    for key, value in updates.items():
        setattr(app, key, value)
    app.updated_at = datetime.now(UTC)

    session.add(app)
    session.commit()
    session.refresh(app)
    return app


@router.delete("/{application_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
def delete_application(
    application_id: str,
    _: User = Depends(require_current_user),
    session: Session = Depends(get_session),
) -> Response:
    app = session.get(Application, application_id)
    if app is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")

    session.delete(app)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
