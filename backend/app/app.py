from fastapi import Depends, FastAPI
from starlette.staticfiles import StaticFiles

from backend.api.router import router
from backend.app.dependencies import service_manager


def create_app() -> FastAPI:
    app = FastAPI()
    app.include_router(router, dependencies=[Depends(service_manager)])
    app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
    return app
