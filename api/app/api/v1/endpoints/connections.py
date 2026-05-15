from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, and_, desc, or_, select

from app.api.v1.endpoints.auth import require_current_user
from app.core.db import get_session
from app.models.connector import ConnectorConnection, ConnectorSyncCheckpoint, ConnectorSyncRun, ConnectorType
from app.models.identity import OdsIdentityComputer, OdsIdentityUser
from app.models.user import User
from app.services.active_directory import ActiveDirectoryClient, parse_ad_config
from app.schemas.connector import (
    ConnectionCreate,
    ConnectionRead,
    ConnectionSyncCheckpointPage,
    ConnectionSyncCheckpointRead,
    ConnectionSyncRunPage,
    ConnectionSyncRequest,
    ConnectionSyncResponse,
    ConnectionSyncRunRead,
    ConnectionTestResponse,
    CursorPageMeta,
)

router = APIRouter()


def _build_ad_client(connection: ConnectorConnection) -> ActiveDirectoryClient:
    return ActiveDirectoryClient(parse_ad_config(connection.config_json))


def _to_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


@router.post("/{connection_id}/test", response_model=ConnectionTestResponse)
def test_connection(
    connection_id: str,
    _: User = Depends(require_current_user),
    session: Session = Depends(get_session),
) -> ConnectionTestResponse:
    connection = session.get(ConnectorConnection, connection_id)
    if connection is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Connection not found")

    connector_type = session.get(ConnectorType, connection.connector_type_id)
    connector_slug = connector_type.slug if connector_type else "unknown"
    if connector_slug != "active_directory":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Connection test is currently supported only for active_directory",
        )

    try:
        _build_ad_client(connection).test_connection()
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"AD connection failed: {exc}") from exc

    return ConnectionTestResponse(
        connection_id=connection.id,
        connector_type_slug=connector_slug,
        status="ok",
        message="LDAP bind and connection check succeeded",
    )


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

    connector_type = session.get(ConnectorType, connection.connector_type_id)
    connector_slug = connector_type.slug if connector_type else "unknown"
    if connector_slug != "active_directory":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sync is currently supported only for active_directory",
        )

    if payload.entity_name not in {"users", "computers"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Supported entities are: users, computers",
        )

    now = datetime.now(UTC)
    existing_checkpoint = session.exec(
        select(ConnectorSyncCheckpoint).where(
            ConnectorSyncCheckpoint.connection_id == connection.id,
            ConnectorSyncCheckpoint.entity_name == payload.entity_name,
        )
    ).first()
    watermark_before = existing_checkpoint.cursor_value if existing_checkpoint else None
    watermark_after = payload.cursor_value
    if watermark_after is None:
        watermark_after = now.isoformat()

    client = _build_ad_client(connection)
    try:
        records = client.fetch_users() if payload.entity_name == "users" else client.fetch_computers()
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"AD sync failed: {exc}") from exc

    records_read = 0
    records_written = 0
    records_failed = 0
    last_seen_at = datetime.now(UTC)
    for row in records:
        records_read += 1
        source_object_id = str(row.get("objectGUID") or row.get("object_guid") or "").strip()
        if not source_object_id:
            records_failed += 1
            continue

        if payload.entity_name == "users":
            existing = session.exec(
                select(OdsIdentityUser).where(
                    OdsIdentityUser.connection_id == connection.id,
                    OdsIdentityUser.source_object_id == source_object_id,
                )
            ).first()
            if existing is None:
                existing = OdsIdentityUser(
                    org_id=connection.org_id,
                    connection_id=connection.id,
                    source_object_id=source_object_id,
                    created_at=last_seen_at,
                )
            existing.distinguished_name = row.get("distinguishedName")
            existing.user_principal_name = row.get("userPrincipalName")
            existing.sam_account_name = row.get("sAMAccountName")
            existing.display_name = row.get("displayName")
            existing.mail = row.get("mail")
            existing.department = row.get("department")
            existing.title = row.get("title")
            uac = int(row.get("userAccountControl") or 0)
            existing.account_enabled = (uac & 2) == 0
            existing.source_created_at = _to_datetime(row.get("whenCreated"))
            existing.source_updated_at = _to_datetime(row.get("whenChanged"))
            existing.last_seen_at = last_seen_at
            existing.is_deleted = False
            existing.deleted_at = None
            existing.raw_payload_json = row
            existing.updated_at = last_seen_at
            session.add(existing)
            records_written += 1
        else:
            existing = session.exec(
                select(OdsIdentityComputer).where(
                    OdsIdentityComputer.connection_id == connection.id,
                    OdsIdentityComputer.source_object_id == source_object_id,
                )
            ).first()
            if existing is None:
                existing = OdsIdentityComputer(
                    org_id=connection.org_id,
                    connection_id=connection.id,
                    source_object_id=source_object_id,
                    created_at=last_seen_at,
                )
            existing.distinguished_name = row.get("distinguishedName")
            existing.dns_host_name = row.get("dNSHostName")
            existing.sam_account_name = row.get("sAMAccountName")
            existing.operating_system = row.get("operatingSystem")
            existing.operating_system_version = row.get("operatingSystemVersion")
            uac = int(row.get("userAccountControl") or 0)
            existing.account_enabled = (uac & 2) == 0
            existing.source_created_at = _to_datetime(row.get("whenCreated"))
            existing.source_updated_at = _to_datetime(row.get("whenChanged"))
            existing.last_seen_at = last_seen_at
            existing.is_deleted = False
            existing.deleted_at = None
            existing.raw_payload_json = row
            existing.updated_at = last_seen_at
            session.add(existing)
            records_written += 1

    sync_run = ConnectorSyncRun(
        org_id=connection.org_id,
        connection_id=connection.id,
        run_type="manual_full",
        status="completed",
        started_at=now,
        ended_at=now,
        watermark_before=watermark_before,
        watermark_after=watermark_after,
        records_read=records_read,
        records_written=records_written,
        records_failed=records_failed,
        metadata_json={"entity_name": payload.entity_name},
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
