from json import JSONDecodeError

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from pydantic import ValidationError
from starlette.responses import JSONResponse, RedirectResponse, Response
from starlette.templating import Jinja2Templates

from backend.app import dependencies
from backend.app.services import Services

router = APIRouter(prefix="/admin")
INTERFACE_TAG = "Admin Interface"
API_TAG = "Admin API"


def require_admin_session(request: Request) -> None:
    if not dependencies.services().auth.has_admin_session(request):
        raise HTTPException(status_code=401, detail="Not authorized")


@router.get("/", tags=[INTERFACE_TAG])
async def get_main_page(
    request: Request,
    templates: Jinja2Templates = Depends(dependencies.templates),
    services: Services = Depends(dependencies.services),
) -> Response:
    if not services.auth.has_admin_session(request):
        return RedirectResponse(router.url_path_for(get_login_page.__name__), 308)

    return templates.TemplateResponse("admin/admin.html", {"request": request})


@router.get("/login", tags=[INTERFACE_TAG])
async def get_login_page(
    request: Request,
    services: Services = Depends(dependencies.services),
    templates: Jinja2Templates = Depends(dependencies.templates),
) -> Response:
    if services.auth.has_admin_session(request):
        return RedirectResponse(router.url_path_for(get_main_page.__name__), 303)
    return templates.TemplateResponse(
        "admin/login.html", {"request": request, "is_warning_hidden": True}
    )


@router.post("/login", tags=[INTERFACE_TAG])
async def post_login_form(
    request: Request,
    password: str = Form(default=""),
    services: Services = Depends(dependencies.services),
    templates: Jinja2Templates = Depends(dependencies.templates),
) -> Response:
    if not services.auth.is_admin_password(password):
        return templates.TemplateResponse(
            "admin/login.html", {"request": request, "is_warning_hidden": False}
        )
    response = RedirectResponse(router.url_path_for(get_main_page.__name__), 303)
    services.auth.set_admin_session(response)
    return response


@router.post("/auth", tags=[API_TAG], response_class=JSONResponse)
async def authenticate(
    request: Request,
    services: Services = Depends(dependencies.services),
) -> JSONResponse:
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
    if not services.auth.is_admin_password(password):
        raise HTTPException(status_code=401, detail="Incorrect password")
    response_content = {"token": services.auth.create_admin_session_token()}
    return JSONResponse(response_content)


@router.get("/revision", tags=[API_TAG], response_class=JSONResponse)
async def get_revision_info(
    request: Request,
    services: Services = Depends(dependencies.services),
) -> JSONResponse:
    require_admin_session(request)

    revision = services.storage.revision
    response_content = revision.to_json()
    for key in list(response_content.keys()):
        if response_content[key] is None:
            response_content.pop(key)
    return JSONResponse(content=response_content)


@router.post("/revision/start", tags=[API_TAG], response_class=JSONResponse)
async def request_storage_update(
    request: Request,
    services: Services = Depends(dependencies.services),
) -> JSONResponse:
    require_admin_session(request)

    response_content = {"response": services.storage.request_update().value}
    return JSONResponse(content=response_content)


@router.post("/revision/pause", tags=[API_TAG], response_class=JSONResponse)
async def request_storage_update_pause(
    request: Request,
    services: Services = Depends(dependencies.services),
) -> JSONResponse:
    require_admin_session(request)

    response_content = {"response": services.storage.request_update_pause().value}
    return JSONResponse(content=response_content)


@router.post("/revision/cancel", tags=[API_TAG], response_class=JSONResponse)
async def request_storage_update_cancellation(
    request: Request,
    services: Services = Depends(dependencies.services),
) -> JSONResponse:
    require_admin_session(request)

    response_content = {
        "response": services.storage.request_update_cancellation().value
    }
    return JSONResponse(content=response_content)
