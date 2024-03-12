from json import JSONDecodeError

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import ValidationError
from starlette.responses import HTMLResponse, JSONResponse, PlainTextResponse
from starlette.templating import Jinja2Templates

from backend.app import dependencies
from backend.app.services import Services

router = APIRouter()


@router.get("/", tags=["Client interface"], response_class=HTMLResponse)
async def get_main_page(
    request: Request, templates: Jinja2Templates = Depends(dependencies.templates)
) -> HTMLResponse:
    return templates.TemplateResponse("client/client.html", {"request": request})


@router.get("/range/{prefix}", tags=["Client API"], response_class=PlainTextResponse)
async def get_range(
    prefix: str, services: Services = Depends(dependencies.services)
) -> PlainTextResponse:
    try:
        records = await services.storage.get_range(prefix)
        return PlainTextResponse(records, status_code=200)
    except ValueError as error:
        return PlainTextResponse(str(error), status_code=400)


@router.post("/strength", tags=["Client API"], response_class=JSONResponse)
async def check_strength(
    request: Request, services: Services = Depends(dependencies.services)
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
    if len(password) > 100:
        raise HTTPException(
            status_code=400, detail="Password length must be 100 characters or less."
        )
    result = services.strength_checker.check(password)
    response_content = {
        "strength": result.strength.value,
        "violated_rules": [rule.value for rule in result.violated_rules],
    }
    return JSONResponse(content=response_content)
