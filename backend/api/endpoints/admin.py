from fastapi import APIRouter, Depends, Request
from starlette.responses import JSONResponse, Response
from starlette.templating import Jinja2Templates

from backend.app import dependencies
from backend.app.service_manager import ServiceManager

router = APIRouter()


@router.get("/")
async def get_admin_page(
    request: Request, templates: Jinja2Templates = Depends(dependencies.templates)
) -> Response:
    return templates.TemplateResponse("admin-page.html", {"request": request})


@router.get("/revision")
async def get_revision_info(
    services: ServiceManager = Depends(dependencies.service_manager),
) -> Response:
    revision = services.storage.revision
    response_content = {
        "status": revision.status.value,
        "start_ts": revision.start_ts,
        "end_ts": revision.end_ts,
        "progress": revision.progress,
        "error_message": revision.error and str(revision.error),
    }
    for key in list(response_content.keys()):
        if response_content[key] is None:
            response_content.pop(key)
    return JSONResponse(content=response_content)


@router.post("/revision/start")
async def request_storage_update(
    services: ServiceManager = Depends(dependencies.service_manager),
) -> Response:
    response_content = {"response": services.storage.request_update().value}
    return JSONResponse(content=response_content)


@router.post("/revision/cancel")
async def request_storage_update_cancellation(
    services: ServiceManager = Depends(dependencies.service_manager),
) -> Response:
    response_content = {
        "response": services.storage.request_update_cancellation().value
    }
    return JSONResponse(content=response_content)
