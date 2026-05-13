from fastapi import APIRouter, Depends

from app.api.v1.endpoints.applications import router as applications_router
from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.connections import router as connections_router
from app.api.v1.endpoints.databases import router as databases_router
from app.api.v1.endpoints.eav import router as eav_router
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.users import router as users_router
from app.api.versioning import require_api_version

api_router = APIRouter(dependencies=[Depends(require_api_version)])
api_router.include_router(health_router, tags=["Health"])
api_router.include_router(users_router, prefix="/users", tags=["Users"])
api_router.include_router(auth_router, prefix="/auth", tags=["Auth"])
api_router.include_router(applications_router, prefix="/applications", tags=["Applications"])
api_router.include_router(databases_router, prefix="/databases", tags=["Databases"])
api_router.include_router(connections_router, prefix="/connections", tags=["Connections"])
api_router.include_router(eav_router)
