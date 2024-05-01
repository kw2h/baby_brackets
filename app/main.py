import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware

from app import settings
from app.models import HealthCheck
from app.routers import endpoints, views, login, partials


app = FastAPI(
    title=settings.project_name,
    version=settings.version,
    openapi_url=f"{settings.api_v1_prefix}/openapi.json",
    debug=settings.debug,
    middleware=[Middleware(SessionMiddleware, secret_key=settings.secret_key)]
)


app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_model=HealthCheck, tags=["status"])
async def health_check():
    return {
        "name": settings.project_name,
        "version": settings.version,
        "description": settings.description
    }


app.include_router(endpoints.user_router, prefix=settings.api_v1_prefix)
app.include_router(endpoints.parentbracket_router, prefix=settings.api_v1_prefix)
app.include_router(endpoints.bracket_router, prefix=settings.api_v1_prefix)
app.include_router(endpoints.matchup_router, prefix=settings.api_v1_prefix)
app.include_router(endpoints.name_router, prefix=settings.api_v1_prefix)
app.include_router(endpoints.namemtchuplink_router, prefix=settings.api_v1_prefix)
app.include_router(views.router)
app.include_router(login.router)
app.include_router(partials.router)


@app.exception_handler(HTTPException)
def auth_exception_handler(request: Request, exc: HTTPException):
    """
    Redirect the user to the login page if not logged in
    """
    return RedirectResponse(url="/auth/login")


if __name__ == '__main__':
    uvicorn.run("main:app", port=8080, host="0.0.0.0", reload=True)