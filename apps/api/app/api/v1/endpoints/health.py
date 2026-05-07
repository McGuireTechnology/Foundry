from fastapi import APIRouter
from sqlmodel import Session, select

from app.core.db import engine

router = APIRouter()


@router.get("/health")
async def health() -> dict[str, str]:
    with Session(engine) as session:
        session.exec(select(1))
    return {"status": "ok"}
