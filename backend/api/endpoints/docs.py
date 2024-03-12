from fastapi import APIRouter, Depends, Request
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates

from backend.app import dependencies

router = APIRouter()


@router.get("/docs", tags=["Documentation interface"], response_class=HTMLResponse)
async def docs(
    request: Request, templates: Jinja2Templates = Depends(dependencies.templates)
) -> HTMLResponse:
    return templates.TemplateResponse("docs.html", {"request": request})
