from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from api.routers.health import router
from api.routers.marketing import router as marketing_router
from api.routers.sales import router as sales_router
from api.routers.tech import router as tech_router
from api.routers.approval import router as approval_router
from api.routers.executions import router as executions_router
from api.routers.resources import router as resources_router
from exceptions.exceptions import (
    ConduitException,
    InvalidStateTransitionException,
    ResourceAlreadyExist,
    ResourceNotFoundException,
)

app=FastAPI()


@app.exception_handler(ConduitException)
async def handle_conduit_exception(request, exc: ConduitException):
    if isinstance(exc, ResourceNotFoundException):
        status_code = 404
    elif isinstance(exc, (ResourceAlreadyExist, InvalidStateTransitionException)):
        status_code = 409
    else:
        status_code = 400
    return JSONResponse(status_code=status_code, content={"detail": exc.message})


app.include_router(router)
app.include_router(marketing_router)
app.include_router(sales_router)
app.include_router(tech_router)
app.include_router(approval_router)
app.include_router(executions_router)
app.include_router(resources_router)

frontend_dir = Path(__file__).parent / "frontend"


class NoCacheStaticFiles(StaticFiles):
    async def get_response(self, path, scope):
        response = await super().get_response(path, scope)
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        return response


if frontend_dir.is_dir():
    app.mount("/assets", NoCacheStaticFiles(directory=frontend_dir), name="frontend-assets")

    @app.get("/", include_in_schema=False)
    def frontend_index():
        response = FileResponse(frontend_dir / "index.html")
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        return response

    @app.get("/{frontend_path:path}", include_in_schema=False)
    def frontend_fallback(frontend_path: str):
        if frontend_path.startswith(("api/", "docs", "openapi.json", "redoc")):
            raise HTTPException(status_code=404, detail="Not found")
        response = FileResponse(frontend_dir / "index.html")
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        return response
