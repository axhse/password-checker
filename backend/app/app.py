from fastapi import Depends, FastAPI
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
from starlette.staticfiles import StaticFiles

from backend.api.router import router
from backend.app.dependencies import service_manager
from backend.app.environment import EnvKey, get_env_value


def create_app() -> FastAPI:
    app = FastAPI()
    if get_env_value(EnvKey.HTTPS_ONLY, bool):
        app.add_middleware(HTTPSRedirectMiddleware)
    app.include_router(router, dependencies=[Depends(service_manager)])
    app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
    return app
