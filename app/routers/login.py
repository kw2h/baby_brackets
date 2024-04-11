from datetime import timedelta
from fastapi import APIRouter, Depends, Request, HTTPException, status, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Annotated, Any, Dict

from app import templates, forms, settings
from app.auth import authenticate_user, create_access_token, get_session_from_token
from app.database import get_async_session
from app.models import Token, SessionToken


# --------------------------------------------------------------------------------
# Router
# --------------------------------------------------------------------------------

router = APIRouter()


# --------------------------------------------------------------------------------
# Routes
# --------------------------------------------------------------------------------
@router.post("/token_bearer", tags=["Auth"])
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


@router.post("/token_cookie", tags=["Auth"])
async def login_for_cookie_access_token(
    response: Response, 
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_async_session)
) -> Dict[str, str]:
    user = await authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    session_token: SessionToken = SessionToken(username=user.username)
    db.add(session_token)
    await db.commit()
    await db.refresh(session_token)
    access_token = create_access_token(
        data={
            "session_id": session_token.session_id,
            "username": session_token.username
        }
    )
    response.set_cookie(
        key=settings.cookie_name, 
        value=f"Bearer {access_token}", 
        httponly=True  # prevents JavaScript from reading the cookie
    )  
    return {settings.cookie_name: access_token, "token_type": "bearer"}


@router.get("/auth/login", tags=["Auth"])
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


@router.post("/auth/login", tags=["Auth"])
async def post_login(
    request: Request,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: AsyncSession = Depends(get_async_session)
):
    form = forms.LoginForm(request)
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


@router.get("/auth/logout", tags=["Auth"], response_class=HTMLResponse)
async def logout(
    session_token: SessionToken = Depends(get_session_from_token),
    db: AsyncSession = Depends(get_async_session)
):  
    response = RedirectResponse("/index", status.HTTP_302_FOUND)
    response.delete_cookie(settings.cookie_name)
    await db.delete(session_token)
    await db.commit()
    return response
