from datetime import timedelta
from fastapi import APIRouter, Depends, Request, HTTPException, status, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Annotated, Any, Dict

from app import templates, forms, settings
from app.auth import get_user, authenticate_user, create_access_token
from app.database import get_async_session
from app.models import Token


# --------------------------------------------------------------------------------
# Router
# --------------------------------------------------------------------------------

router = APIRouter()


# --------------------------------------------------------------------------------
# Routes
# --------------------------------------------------------------------------------
@router.post("/token_bearer")
async def login_for_bearer_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: AsyncSession = Depends(get_async_session)
) -> Token:
    user = await authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@router.post("/token_cookie")
async def login_for_cookie_access_token(
    response: Response, 
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_async_session)
) -> Dict[str, str]:
    user = await authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    access_token = create_access_token(data={"username": user.username})
    
    response.set_cookie(
        key=settings.cookie_name, 
        value=f"Bearer {access_token}", 
        httponly=True  # prevents JavaScript from reading the cookie
    )  
    return {settings.cookie_name: access_token, "token_type": "bearer"}


@router.get("/login", tags=["Pages"])
async def get_login(request: Request) -> Any:
    form = forms.LoginForm(request)
    return templates.TemplateResponse(
        "pages/login.html",
        context={
            "request": request,
            "form": form,
            "errors": []
        }
    )


@router.post("/login", tags=["Pages"])
async def post_login(
    request: Request,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: AsyncSession = Depends(get_async_session)
):
    form = forms.LoginForm(request)
    # user = await get_user(username=form_data.username, db=db)
    # user = await authenticate_user(form_data.username, form_data.password, db)
    # if not user:
    #     return RedirectResponse("/login", status.HTTP_302_FOUND)

    response = RedirectResponse("/index", status.HTTP_302_FOUND)
    try:
        await login_for_cookie_access_token(response=response, form_data=form_data, db=db)
    except HTTPException:
        return templates.TemplateResponse(
            "pages/login.html",
            context={
                "request": request,
                "form": form,
                "errors": ["Incorrect Email or Password"]
            }
        )

    return response
    