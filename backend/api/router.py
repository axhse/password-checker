from fastapi import APIRouter

from backend.api.endpoints import admin, client

router = APIRouter()
router.include_router(client.router, tags=["client"])
router.include_router(admin.router, prefix="/admin", tags=["admin"])
