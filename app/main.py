import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app import settings
from app.models import HealthCheck
from app.routers.endpoints import (user_router, parentbracket_router, 
                                  bracket_router, matchup_router,
                                  name_router, namemtchuplink_router)
from app.routers import root, login

app = FastAPI(
    title=settings.project_name,
    version=settings.version,
    openapi_url=f"{settings.api_v1_prefix}/openapi.json",
    debug=settings.debug
)


app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_model=HealthCheck, tags=["status"])
async def health_check():
    return {
        "name": settings.project_name,
        "version": settings.version,
        "description": settings.description
    }


app.include_router(user_router, prefix=settings.api_v1_prefix)
app.include_router(parentbracket_router, prefix=settings.api_v1_prefix)
app.include_router(bracket_router, prefix=settings.api_v1_prefix)
app.include_router(matchup_router, prefix=settings.api_v1_prefix)
app.include_router(name_router, prefix=settings.api_v1_prefix)
app.include_router(namemtchuplink_router, prefix=settings.api_v1_prefix)
app.include_router(root.router)
app.include_router(login.router)



if __name__ == '__main__':
    uvicorn.run("main:app", port=8080, host="0.0.0.0", reload=True)