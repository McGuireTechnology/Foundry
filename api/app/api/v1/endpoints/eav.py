from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlmodel import Session, select

from app.api.v1.endpoints.auth import require_current_user
from app.core.db import get_session
from app.models.application import Application
from app.models.eav import AttributeValue, DataAttribute, DataEntity, EntityRecord
from app.models.user import User
from app.schemas.eav import (
    AttributeValueInput,
    AttributeValueRead,
    DataAttributeCreate,
    DataAttributeRead,
    DataAttributeUpdate,
    DataEntityCreate,
    DataEntityRead,
    DataEntityUpdate,
    EntityRecordCreate,
    EntityRecordRead,
    EntityRecordWithValuesRead,
)

router = APIRouter()


@router.post("/tables", response_model=DataEntityRead, status_code=status.HTTP_201_CREATED, tags=["Tables"])
def create_entity(
    payload: DataEntityCreate,
    _: User = Depends(require_current_user),
    session: Session = Depends(get_session),
) -> DataEntityRead:
    app = session.get(Application, payload.application_id)
    if app is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")
    existing = session.exec(
        select(DataEntity).where(
            DataEntity.application_id == payload.application_id,
            DataEntity.api_name == payload.api_name,
        )
    ).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Entity api_name already exists")
    entity = DataEntity(**payload.model_dump())
    session.add(entity)
    session.commit()
    session.refresh(entity)
    return entity


@router.get("/tables", response_model=list[DataEntityRead], tags=["Tables"])
def list_entities(
    _: User = Depends(require_current_user),
    application_id: str | None = Query(default=None),
    session: Session = Depends(get_session),
) -> list[DataEntityRead]:
    stmt = select(DataEntity)
    if application_id:
        stmt = stmt.where(DataEntity.application_id == application_id)
    return list(session.exec(stmt).all())


@router.patch("/tables/{entity_id}", response_model=DataEntityRead, tags=["Tables"])
def update_entity(
    entity_id: str,
    payload: DataEntityUpdate,
    _: User = Depends(require_current_user),
    session: Session = Depends(get_session),
) -> DataEntityRead:
    entity = session.get(DataEntity, entity_id)
    if entity is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entity not found")
    updates = payload.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(entity, key, value)
    entity.updated_at = datetime.now(UTC)
    session.add(entity)
    session.commit()
    session.refresh(entity)
    return entity


@router.post("/columns", response_model=DataAttributeRead, status_code=status.HTTP_201_CREATED, tags=["Columns"])
def create_attribute(
    payload: DataAttributeCreate,
    _: User = Depends(require_current_user),
    session: Session = Depends(get_session),
) -> DataAttributeRead:
    entity = session.get(DataEntity, payload.entity_id)
    if entity is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entity not found")
    existing = session.exec(
        select(DataAttribute).where(
            DataAttribute.entity_id == payload.entity_id,
            DataAttribute.api_name == payload.api_name,
        )
    ).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Attribute api_name already exists")
    attribute = DataAttribute(**payload.model_dump())
    session.add(attribute)
    session.commit()
    session.refresh(attribute)
    return attribute


@router.get("/columns", response_model=list[DataAttributeRead], tags=["Columns"])
def list_attributes(
    _: User = Depends(require_current_user),
    entity_id: str | None = Query(default=None),
    session: Session = Depends(get_session),
) -> list[DataAttributeRead]:
    stmt = select(DataAttribute)
    if entity_id:
        stmt = stmt.where(DataAttribute.entity_id == entity_id)
    return list(session.exec(stmt).all())


@router.get("/tables/{entity_id}/columns", response_model=list[DataAttributeRead], tags=["Columns"])
def list_columns_for_table(
    entity_id: str,
    _: User = Depends(require_current_user),
    session: Session = Depends(get_session),
) -> list[DataAttributeRead]:
    entity = session.get(DataEntity, entity_id)
    if entity is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Table not found")
    return list(session.exec(select(DataAttribute).where(DataAttribute.entity_id == entity_id)).all())


@router.patch("/columns/{attribute_id}", response_model=DataAttributeRead, tags=["Columns"])
def update_attribute(
    attribute_id: str,
    payload: DataAttributeUpdate,
    _: User = Depends(require_current_user),
    session: Session = Depends(get_session),
) -> DataAttributeRead:
    attribute = session.get(DataAttribute, attribute_id)
    if attribute is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attribute not found")
    updates = payload.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(attribute, key, value)
    attribute.updated_at = datetime.now(UTC)
    session.add(attribute)
    session.commit()
    session.refresh(attribute)
    return attribute


def _upsert_record_values(session: Session, record_id: str, values: list[AttributeValueInput]) -> None:
    for value_payload in values:
        attribute = session.get(DataAttribute, value_payload.attribute_id)
        if attribute is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attribute not found")
        existing = session.exec(
            select(AttributeValue).where(
                AttributeValue.record_id == record_id,
                AttributeValue.attribute_id == value_payload.attribute_id,
            )
        ).first()
        row_data = value_payload.model_dump()
        if existing:
            existing.value_text = row_data["value_text"]
            existing.value_number = row_data["value_number"]
            existing.value_boolean = row_data["value_boolean"]
            existing.value_datetime = row_data["value_datetime"]
            existing.value_json = row_data["value_json"]
            existing.updated_at = datetime.now(UTC)
            session.add(existing)
        else:
            session.add(AttributeValue(record_id=record_id, **row_data))


@router.post("/records", response_model=EntityRecordWithValuesRead, status_code=status.HTTP_201_CREATED, tags=["Records"])
def create_record(
    payload: EntityRecordCreate,
    _: User = Depends(require_current_user),
    session: Session = Depends(get_session),
) -> EntityRecordWithValuesRead:
    entity = session.get(DataEntity, payload.entity_id)
    if entity is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entity not found")
    record = EntityRecord(entity_id=payload.entity_id)
    session.add(record)
    session.commit()
    session.refresh(record)
    _upsert_record_values(session, record.id, payload.values)
    session.commit()
    values = list(session.exec(select(AttributeValue).where(AttributeValue.record_id == record.id)).all())
    return EntityRecordWithValuesRead(record=EntityRecordRead.model_validate(record), values=[AttributeValueRead.model_validate(v) for v in values])


@router.get("/records", response_model=list[EntityRecordRead], tags=["Records"])
def list_records(
    _: User = Depends(require_current_user),
    table_id: str | None = Query(default=None),
    session: Session = Depends(get_session),
) -> list[EntityRecordRead]:
    stmt = select(EntityRecord)
    if table_id:
        stmt = stmt.where(EntityRecord.entity_id == table_id)
    return [EntityRecordRead.model_validate(v) for v in session.exec(stmt).all()]


@router.get("/tables/{entity_id}/records", response_model=list[EntityRecordRead], tags=["Records"])
def list_records_for_table(
    entity_id: str,
    _: User = Depends(require_current_user),
    session: Session = Depends(get_session),
) -> list[EntityRecordRead]:
    entity = session.get(DataEntity, entity_id)
    if entity is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Table not found")
    return [EntityRecordRead.model_validate(v) for v in session.exec(select(EntityRecord).where(EntityRecord.entity_id == entity_id)).all()]


@router.get("/records/{record_id}", response_model=EntityRecordWithValuesRead, tags=["Records"])
def get_record(
    record_id: str,
    _: User = Depends(require_current_user),
    session: Session = Depends(get_session),
) -> EntityRecordWithValuesRead:
    record = session.get(EntityRecord, record_id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")
    values = list(session.exec(select(AttributeValue).where(AttributeValue.record_id == record.id)).all())
    return EntityRecordWithValuesRead(record=EntityRecordRead.model_validate(record), values=[AttributeValueRead.model_validate(v) for v in values])


@router.post("/values", response_model=list[AttributeValueRead], status_code=status.HTTP_201_CREATED, tags=["Values"])
def upsert_values(
    payload: list[AttributeValueInput],
    record_id: str = Query(...),
    _: User = Depends(require_current_user),
    session: Session = Depends(get_session),
) -> list[AttributeValueRead]:
    record = session.get(EntityRecord, record_id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")
    _upsert_record_values(session, record_id, payload)
    record.updated_at = datetime.now(UTC)
    session.add(record)
    session.commit()
    return [AttributeValueRead.model_validate(v) for v in session.exec(select(AttributeValue).where(AttributeValue.record_id == record_id)).all()]


@router.patch("/records/{record_id}/values", response_model=EntityRecordWithValuesRead, tags=["Values"])
def patch_record_values(
    record_id: str,
    payload: list[AttributeValueInput],
    _: User = Depends(require_current_user),
    session: Session = Depends(get_session),
) -> EntityRecordWithValuesRead:
    record = session.get(EntityRecord, record_id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")
    _upsert_record_values(session, record_id, payload)
    record.updated_at = datetime.now(UTC)
    session.add(record)
    session.commit()
    session.refresh(record)
    values = list(session.exec(select(AttributeValue).where(AttributeValue.record_id == record.id)).all())
    return EntityRecordWithValuesRead(record=EntityRecordRead.model_validate(record), values=[AttributeValueRead.model_validate(v) for v in values])


@router.get("/values", response_model=list[AttributeValueRead], tags=["Values"])
def list_values(
    _: User = Depends(require_current_user),
    record_id: str | None = Query(default=None),
    column_id: str | None = Query(default=None),
    session: Session = Depends(get_session),
) -> list[AttributeValueRead]:
    stmt = select(AttributeValue)
    if record_id:
        stmt = stmt.where(AttributeValue.record_id == record_id)
    if column_id:
        stmt = stmt.where(AttributeValue.attribute_id == column_id)
    return [AttributeValueRead.model_validate(v) for v in session.exec(stmt).all()]


@router.get("/records/{record_id}/values", response_model=list[AttributeValueRead], tags=["Values"])
def list_values_for_record(
    record_id: str,
    _: User = Depends(require_current_user),
    session: Session = Depends(get_session),
) -> list[AttributeValueRead]:
    record = session.get(EntityRecord, record_id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")
    return [AttributeValueRead.model_validate(v) for v in session.exec(select(AttributeValue).where(AttributeValue.record_id == record_id)).all()]


@router.get("/columns/{column_id}/values", response_model=list[AttributeValueRead], tags=["Values"])
def list_values_for_column(
    column_id: str,
    _: User = Depends(require_current_user),
    session: Session = Depends(get_session),
) -> list[AttributeValueRead]:
    column = session.get(DataAttribute, column_id)
    if column is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Column not found")
    return [AttributeValueRead.model_validate(v) for v in session.exec(select(AttributeValue).where(AttributeValue.attribute_id == column_id)).all()]


@router.delete("/records/{record_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response, tags=["Records"])
def delete_record(
    record_id: str,
    _: User = Depends(require_current_user),
    session: Session = Depends(get_session),
) -> Response:
    record = session.get(EntityRecord, record_id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")
    values = list(session.exec(select(AttributeValue).where(AttributeValue.record_id == record.id)).all())
    for value in values:
        session.delete(value)
    session.delete(record)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
