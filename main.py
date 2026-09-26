from fastapi import FastAPI
from api.routers.health import router
from api.routers.marketing import router as marketing_router
from api.routers.sales import router as sales_router
from api.routers.tech import router as tech_router
app=FastAPI()
app.include_router(router)
app.include_router(marketing_router)
app.include_router(sales_router)
app.include_router(tech_router)