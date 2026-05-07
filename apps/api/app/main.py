from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.db import init_db


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name)
    app.include_router(api_router, prefix=settings.api_v1_prefix)

    @app.on_event("startup")
    def on_startup() -> None:
        init_db()

    return app


app = create_app()
