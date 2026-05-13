from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, and_, desc, or_, select

from app.api.v1.endpoints.auth import require_current_user
from app.core.db import get_session
from app.models.connector import ConnectorConnection, ConnectorSyncCheckpoint, ConnectorSyncRun, ConnectorType
from app.models.user import User
from app.schemas.connector import (
    ConnectionCreate,
    ConnectionRead,
    ConnectionSyncCheckpointPage,
    ConnectionSyncCheckpointRead,
    ConnectionSyncRunPage,
    ConnectionSyncRequest,
    ConnectionSyncResponse,
    ConnectionSyncRunRead,
    CursorPageMeta,
)

router = APIRouter()


@router.post("", response_model=ConnectionRead, status_code=status.HTTP_201_CREATED)
def create_connection(
    payload: ConnectionCreate,
    _: User = Depends(require_current_user),
    session: Session = Depends(get_session),
) -> ConnectionRead:
    existing_connection = session.exec(
        select(ConnectorConnection).where(
            ConnectorConnection.org_id == payload.org_id,
            ConnectorConnection.slug == payload.slug,
        )
    ).first()
    if existing_connection:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Connection slug already exists for org")

    connector_type = session.exec(select(ConnectorType).where(ConnectorType.slug == payload.connector_type_slug)).first()
    now = datetime.now(UTC)
    if connector_type is None:
        connector_type = ConnectorType(
            slug=payload.connector_type_slug,
            name=payload.connector_type_name or payload.connector_type_slug.replace("_", " ").title(),
            created_at=now,
            updated_at=now,
        )
        session.add(connector_type)
        session.flush()

    connection = ConnectorConnection(
        org_id=payload.org_id,
        connector_type_id=connector_type.id,
        name=payload.name,
        slug=payload.slug,
        config_json=payload.config_json,
        credentials_ref=payload.credentials_ref,
        status="active",
        created_at=now,
        updated_at=now,
    )
    session.add(connection)
    session.commit()
    session.refresh(connection)
    return connection


@router.get("", response_model=list[ConnectionRead])
def list_connections(
    _: User = Depends(require_current_user),
    session: Session = Depends(get_session),
) -> list[ConnectionRead]:
    return list(session.exec(select(ConnectorConnection)).all())


@router.get("/{connection_id}/sync-runs", response_model=ConnectionSyncRunPage)
def list_connection_sync_runs(
    connection_id: str,
    limit: int = Query(default=20, ge=1, le=100),
    cursor: str | None = Query(default=None),
    _: User = Depends(require_current_user),
    session: Session = Depends(get_session),
) -> ConnectionSyncRunPage:
    connection = session.get(ConnectorConnection, connection_id)
    if connection is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Connection not found")

    cursor_started_at: datetime | None = None
    cursor_id: str | None = None
    if cursor:
        try:
            started_at_text, cursor_id = cursor.split("|", 1)
            cursor_started_at = datetime.fromisoformat(started_at_text)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid cursor") from exc

    stmt = select(ConnectorSyncRun).where(ConnectorSyncRun.connection_id == connection_id)
    if cursor_started_at and cursor_id:
        stmt = stmt.where(
            or_(
                ConnectorSyncRun.started_at < cursor_started_at,
                and_(ConnectorSyncRun.started_at == cursor_started_at, ConnectorSyncRun.id < cursor_id),
            )
        )

    rows = list(
        session.exec(
            stmt.order_by(desc(ConnectorSyncRun.started_at), desc(ConnectorSyncRun.id)).limit(limit + 1)
        ).all()
    )
    items = rows[:limit]
    next_cursor = None
    if len(rows) > limit:
        tail = items[-1]
        next_cursor = f"{tail.started_at.isoformat()}|{tail.id}"

    return ConnectionSyncRunPage(items=items, page=CursorPageMeta(next_cursor=next_cursor))


@router.get("/{connection_id}/checkpoints", response_model=ConnectionSyncCheckpointPage)
def list_connection_checkpoints(
    connection_id: str,
    limit: int = Query(default=20, ge=1, le=100),
    cursor: str | None = Query(default=None),
    _: User = Depends(require_current_user),
    session: Session = Depends(get_session),
) -> ConnectionSyncCheckpointPage:
    connection = session.get(ConnectorConnection, connection_id)
    if connection is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Connection not found")

    stmt = select(ConnectorSyncCheckpoint).where(ConnectorSyncCheckpoint.connection_id == connection_id)
    if cursor:
        stmt = stmt.where(ConnectorSyncCheckpoint.entity_name > cursor)

    rows = list(
        session.exec(
            stmt.order_by(ConnectorSyncCheckpoint.entity_name, ConnectorSyncCheckpoint.id).limit(limit + 1)
        ).all()
    )
    items = rows[:limit]
    next_cursor = items[-1].entity_name if len(rows) > limit else None

    return ConnectionSyncCheckpointPage(items=items, page=CursorPageMeta(next_cursor=next_cursor))


@router.post("/{connection_id}/sync", response_model=ConnectionSyncResponse, status_code=status.HTTP_202_ACCEPTED)
def sync_connection(
    connection_id: str,
    payload: ConnectionSyncRequest,
    _: User = Depends(require_current_user),
    session: Session = Depends(get_session),
) -> ConnectionSyncResponse:
    connection = session.get(ConnectorConnection, connection_id)
    if connection is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Connection not found")

    now = datetime.now(UTC)
    existing_checkpoint = session.exec(
        select(ConnectorSyncCheckpoint).where(
            ConnectorSyncCheckpoint.connection_id == connection.id,
            ConnectorSyncCheckpoint.entity_name == payload.entity_name,
        )
    ).first()
    watermark_before = existing_checkpoint.cursor_value if existing_checkpoint else None
    watermark_after = payload.cursor_value or now.isoformat()

    sync_run = ConnectorSyncRun(
        org_id=connection.org_id,
        connection_id=connection.id,
        run_type="manual_full",
        status="completed",
        started_at=now,
        ended_at=now,
        watermark_before=watermark_before,
        watermark_after=watermark_after,
        records_read=0,
        records_written=0,
        records_failed=0,
        metadata_json={"stub": True, "entity_name": payload.entity_name},
        created_at=now,
    )
    session.add(sync_run)

    if existing_checkpoint is None:
        existing_checkpoint = ConnectorSyncCheckpoint(
            org_id=connection.org_id,
            connection_id=connection.id,
            entity_name=payload.entity_name,
            cursor_value=watermark_after,
            cursor_updated_at=now,
            updated_at=now,
        )
        session.add(existing_checkpoint)
    else:
        existing_checkpoint.cursor_value = watermark_after
        existing_checkpoint.cursor_updated_at = now
        existing_checkpoint.updated_at = now
        session.add(existing_checkpoint)

    connection.last_synced_at = now
    connection.updated_at = now
    session.add(connection)
    session.commit()
    session.refresh(sync_run)

    return ConnectionSyncResponse(
        run_id=sync_run.id,
        connection_id=connection.id,
        org_id=connection.org_id,
        status=sync_run.status,
        run_type=sync_run.run_type,
        started_at=sync_run.started_at,
        ended_at=sync_run.ended_at or now,
        checkpoint_entity_name=existing_checkpoint.entity_name,
        checkpoint_cursor_value=existing_checkpoint.cursor_value,
    )
