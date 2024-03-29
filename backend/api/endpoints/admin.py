from json import JSONDecodeError

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from pydantic import ValidationError
from starlette.responses import JSONResponse, RedirectResponse, Response
from starlette.templating import Jinja2Templates

from backend.app import dependencies
from backend.app.service_manager import ServiceManager
from backend.services.auth import AuthService

router = APIRouter(prefix="/admin")


def require_admin_session(request: Request) -> None:
    if not dependencies.auth_service().has_admin_session(request):
        raise HTTPException(status_code=401, detail="Not authorized")


@router.get("/")
async def get_admin_page(
    request: Request,
    templates: Jinja2Templates = Depends(dependencies.templates),
    auth_service: AuthService = Depends(dependencies.auth_service),
) -> Response:
    if not auth_service.has_admin_session(request):
        return RedirectResponse(router.url_path_for(get_login_page.__name__), 308)

    return templates.TemplateResponse("admin/admin.html", {"request": request})


@router.get("/revision")
async def get_revision_info(
    request: Request,
    services: ServiceManager = Depends(dependencies.service_manager),
) -> Response:
    require_admin_session(request)

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
    request: Request,
    services: ServiceManager = Depends(dependencies.service_manager),
) -> Response:
    require_admin_session(request)

    response_content = {"response": services.storage.request_update().value}
    return JSONResponse(content=response_content)


@router.post("/revision/cancel")
async def request_storage_update_cancellation(
    request: Request,
    services: ServiceManager = Depends(dependencies.service_manager),
) -> Response:
    require_admin_session(request)

    response_content = {
        "response": services.storage.request_update_cancellation().value
    }
    return JSONResponse(content=response_content)


@router.get("/login")
async def get_login_page(
    request: Request,
    auth_service: AuthService = Depends(dependencies.auth_service),
    templates: Jinja2Templates = Depends(dependencies.templates),
) -> Response:
    if auth_service.has_admin_session(request):
        return RedirectResponse(router.url_path_for(get_admin_page.__name__), 303)
    return templates.TemplateResponse(
        "admin/login.html", {"request": request, "is_warning_hidden": True}
    )


@router.post("/login")
async def post_login_form(
    request: Request,
    password: str = Form(default=""),
    auth_service: AuthService = Depends(dependencies.auth_service),
    templates: Jinja2Templates = Depends(dependencies.templates),
) -> Response:
    if not auth_service.is_admin_password(password):
        return templates.TemplateResponse(
            "admin/login.html", {"request": request, "is_warning_hidden": False}
        )
    response = RedirectResponse(router.url_path_for(get_admin_page.__name__), 303)
    auth_service.set_admin_session(response)
    return response


@router.post("/auth")
async def authenticate(
    request: Request,
    auth_service: AuthService = Depends(dependencies.auth_service),
) -> Response:
    try:
        body_json = await request.json()
    except (ValidationError, JSONDecodeError):
        raise HTTPException(
            status_code=400, detail="Invalid body format: JSON is expected."
        )
    if "password" not in body_json:
        raise HTTPException(
            status_code=400, detail="'password' field is required in the JSON body."
        )
    password = body_json["password"]
    if not isinstance(password, str):
        raise HTTPException(
            status_code=400, detail="'password' field must be a string."
        )
    if not auth_service.is_admin_password(password):
        raise HTTPException(status_code=401, detail="Incorrect password")
    response_content = {"token": auth_service.create_admin_session_token()}
    return JSONResponse(response_content)
