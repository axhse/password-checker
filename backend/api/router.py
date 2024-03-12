from fastapi import APIRouter

from backend.api.endpoints import admin, client, docs

router = APIRouter()
router.include_router(docs.router)
router.include_router(client.router)
router.include_router(admin.router)
