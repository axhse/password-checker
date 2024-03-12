from fastapi import Depends, FastAPI

from backend.api.router import router
from backend.app.dependencies import service_manager

app = FastAPI()
app.include_router(router, dependencies=[Depends(service_manager)])
