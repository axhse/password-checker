from fastapi import Depends, FastAPI
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
from starlette.staticfiles import StaticFiles

from backend.api.router import router
from backend.app.dependencies import services
from backend.app.environment import EnvVar


def create_app() -> FastAPI:
    """
    Create a FastAPI application.
    :return: An application.
    """
    app = FastAPI(openapi_url=None, docs_url=None, redoc_url=None)
    if EnvVar.App.HTTPS_ONLY.get():
        app.add_middleware(HTTPSRedirectMiddleware)
    app.include_router(router, dependencies=[Depends(services)])
    app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
    return app
