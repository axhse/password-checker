from fastapi import APIRouter

from backend.api.endpoints import client

router = APIRouter()
router.include_router(client.router, tags=["client"])
