from fastapi import FastAPI
from api.routers.health import router
from api.routers.marketing import router as marketing_router
app=FastAPI()
app.include_router(router)
app.include_router(marketing_router)