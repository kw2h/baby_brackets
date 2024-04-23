from fastapi import APIRouter, Request, Depends, status, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.exc import IntegrityError
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Annotated

from app import templates, forms
from app.database import get_async_session
from app.auth import  get_session_token_from_cookie, get_session_from_token, get_user
from app.models import UserCreate, User, ParentBracketRead, SessionToken
from app.routers.endpoints import create_user, parentbracket_router


# --------------------------------------------------------------------------------
# Router
# --------------------------------------------------------------------------------

router = APIRouter()


# --------------------------------------------------------------------------------
# Routes
# --------------------------------------------------------------------------------

@router.get("/index", tags=["Pages"])
async def index(request: Request, db: AsyncSession = Depends(get_async_session)):
    try:
        session_token = await get_session_token_from_cookie(request, db)
        user = await get_user(session_token.username, db)
    except:
        session_token = None
        user = None
    return templates.TemplateResponse(
        "pages/index-daisy.html",
        context={
            "request": request,
            "session_token": session_token,
            "user": user
        }
    )


@router.get("/register", tags=["Pages"])
async def register(request: Request):
    form = await forms.RegisterForm.from_formdata(request)
    return templates.TemplateResponse(
        "pages/register-daisy.html",
        context={
            "request": request,
            "form": form,
        }
    )


@router.post("/register", tags=["Pages"])
async def post_register(
    request: Request,
    username: Annotated[str, Form()],
    first_name: Annotated[str, Form()],
    last_name: Annotated[str, Form()],
    password: Annotated[str, Form()],
    pw_confirm: Annotated[str, Form()],
    email: Annotated[str, Form()],
    db: AsyncSession = Depends(get_async_session)
) -> RedirectResponse:  
    form = await forms.RegisterForm.from_formdata(request)
    error_response = templates.TemplateResponse(
        "pages/register-daisy.html",
        context={
            "request": request,
            "form": form,
        }
    )
    if await form.validate_on_submit():
        try:
            user: UserCreate = UserCreate(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password,
            )
            await create_user(user, db)
            return RedirectResponse("/auth/login", status.HTTP_302_FOUND)
        except IntegrityError:
            await db.rollback()
            return error_response
    else:
        return error_response


@router.get("/create", tags=["Pages"])
async def create(
    request: Request,
    session_token: SessionToken = Depends(get_session_from_token)
):
    form = await forms.CreateForm.from_formdata(request)
    return templates.TemplateResponse(
        "pages/create-daisy.html",
        context={
            "request": request,
            "form": form,
            "session_token": session_token
        }
    )


@router.post("/create", tags=["Pages"])
async def post_create(
    request: Request,
    name: Annotated[str, Form()],
    session_token: SessionToken = Depends(get_session_from_token),
    db: AsyncSession = Depends(get_async_session)
) -> RedirectResponse:  
    form = await forms.CreateForm.from_formdata(request)
    error_response = templates.TemplateResponse(
        "pages/create-daisy.html",
        context={
            "request": request,
            "form": form,
            "session_token": session_token
        }
    )
    if await form.validate_on_submit():
        try:
            user: User =  await get_user(session_token.username, db)
            parent_bracket = ParentBracketRead(name=name, completed=False, parent_id=user.id)
            await parentbracket_router._create()(parent_bracket, db=db)
            return RedirectResponse("/setup", status.HTTP_302_FOUND)
        except IntegrityError:
            await db.rollback()
            return error_response
    else:
        return error_response


@router.get("/setup", tags=["Pages"])
async def setup(
    request: Request,
    session_token: SessionToken = Depends(get_session_from_token)
):
    form = await forms.EditForm.from_formdata(request)
    return templates.TemplateResponse(
        "pages/setup-daisy.html",
        context={
            "request": request,
            "form": form,
            "session_token": session_token
        }
    )