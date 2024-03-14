from json import JSONDecodeError

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import ValidationError
from starlette.responses import JSONResponse, PlainTextResponse, Response
from starlette.templating import Jinja2Templates

from backend.app import dependencies
from backend.app.service_manager import ServiceManager

router = APIRouter()


@router.get("/")
async def get_client_page(
    request: Request, templates: Jinja2Templates = Depends(dependencies.templates)
) -> Response:
    return templates.TemplateResponse("client-page.html", {"request": request})


@router.get("/range/{prefix}")
async def get_range(
    prefix: str, services: ServiceManager = Depends(dependencies.service_manager)
) -> Response:
    try:
        records = await services.storage.get_range(prefix)
        return PlainTextResponse(records, status_code=200)
    except ValueError as error:
        return PlainTextResponse(str(error), status_code=400)


@router.post("/strength")
async def check_strength(
    request: Request, services: ServiceManager = Depends(dependencies.service_manager)
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
    result = services.strength_checker.check(password)
    result_json = {
        "strength": result.strength.value,
        "violated_rules": [rule.value for rule in result.violated_rules],
    }
    return JSONResponse(content=result_json)
