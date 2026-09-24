from fastapi import FastAPI
from api.routers.health import router
app=FastAPI()
app.include_router(router)