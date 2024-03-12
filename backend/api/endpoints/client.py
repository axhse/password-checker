from fastapi import APIRouter, Depends
from starlette.responses import PlainTextResponse

from backend.app import dependencies
from backend.app.service_manager import ServiceManager

router = APIRouter()


@router.get("/range/{prefix}")
async def get_range(
    prefix: str, services: ServiceManager = Depends(dependencies.service_manager)
):
    try:
        records = await services.storage.get_range(prefix)
        return PlainTextResponse(records, status_code=200)
    except ValueError as error:
        return PlainTextResponse(str(error), status_code=400)
