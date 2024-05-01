from fastapi import APIRouter, Request, Depends, status, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.exc import IntegrityError
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Annotated

from app import templates, forms, flash
from app.database import get_async_session
from app.auth import  get_session_token_from_cookie, get_session_from_token, get_user
from app.models import (UserCreate, User, ParentBracketRead, ParentBracket,
                        SessionToken, Matchup, Name, NameMatchupLink)
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
    if await form.validate_on_submit() and password == pw_confirm:
        try:
            user: UserCreate = UserCreate(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password,
            )
            await create_user(user, db)
            flash(request, "User Successfully Created", "alert-success")
            return RedirectResponse("/auth/login", status.HTTP_302_FOUND)
        except IntegrityError:
            await db.rollback()
            flash(request, "User already exists", "alert-error")
            return error_response
    else:
        flash(request, "Passwords must match", "alert-error")
        return error_response


@router.get("/create", tags=["Pages"])
async def create(
    request: Request,
    session_token: SessionToken = Depends(get_session_from_token)
):
    if not session_token:
        return "Unauthorized", 404
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
    if not session_token:
        return "Unauthorized", 404
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
            return RedirectResponse(f"/setup?bracket_id={parent_bracket.id}", status.HTTP_302_FOUND)
        except IntegrityError:
            await db.rollback()
            return error_response
    else:
        return error_response


@router.get("/setup", tags=["Pages"])
async def setup(
    request: Request,
    bracket_id: str,
    session_token: SessionToken = Depends(get_session_from_token)
):
    form = await forms.EditForm.from_formdata(request)
    return templates.TemplateResponse(
        "pages/setup-daisy.html",
        context={
            "request": request,
            "form": form,
            "session_token": session_token,
            "bracket_id": bracket_id
        }
    )

@router.post("/setup", tags=["Pages"])
async def post_setup(
    request: Request,
    bracket_id: str,
    name1: Annotated[str, Form()],
    name2: Annotated[str, Form()],
    name3: Annotated[str, Form()],
    name4: Annotated[str, Form()],
    name5: Annotated[str, Form()],
    name6: Annotated[str, Form()],
    name7: Annotated[str, Form()],
    name8: Annotated[str, Form()],
    name9: Annotated[str, Form()],
    name10: Annotated[str, Form()],
    name11: Annotated[str, Form()],
    name12: Annotated[str, Form()],
    name13: Annotated[str, Form()],
    name14: Annotated[str, Form()],
    name15: Annotated[str, Form()],
    name16: Annotated[str, Form()],
    session_token: SessionToken = Depends(get_session_from_token),
    db: AsyncSession = Depends(get_async_session)
) -> RedirectResponse:
    if not session_token:
        return "Unauthorized", 404
    form = await forms.EditForm.from_formdata(request)
    error_response = templates.TemplateResponse(
        "pages/setup-daisy.html",
        context={
            "request": request,
            "form": form,
        }
    )
    if await form.validate_on_submit():
        parent_bracket = await db.get_one(ParentBracket, bracket_id)
        names = [
            (name1, name13),
            (name2, name14),
            (name3, name15),
            (name4, name16),
            (name5, name9),
            (name6, name10),
            (name7, name11),
            (name8, name12),
        ]
        regions = ["east1", "west1", "midwest1", "south1",
                   "east1", "west1", "midwest1", "south1"]
        seeds = [(1,4), (1,4), (1,4), (1,4),
                 (2,3), (2,3), (2,3), (2,3)]
        for region,nms,sds in zip(regions, names, seeds):
            parent_bracket_matchup = Matchup(
                parent_bracket=parent_bracket,
                region=region,
                rnd=1
            )
            for name,seed in zip(nms,sds):
                parent_bracket_matchup_name = Name(
                    name=name,
                    seed=seed
                )
                parent_bracket_matchup_name_link = NameMatchupLink(
                    name=parent_bracket_matchup_name,
                    matchup=parent_bracket_matchup
                )
                db.add(parent_bracket_matchup_name_link)
            db.add(parent_bracket_matchup)

        region_round = [("east2", 2), ("west2", 2), ("midwest2", 2), ("south2", 2),
                        ("finalfour1", 3), ("finalfour2", 3), ("championship", 4)]
        for tup in region_round:
            parent_bracket_matchup = Matchup(
                parent_bracket=parent_bracket, region=tup[0], rnd=tup[1]
            )
            db.add(parent_bracket_matchup)

        # commit to DB:
        await db.commit()
        return RedirectResponse("/index", status.HTTP_302_FOUND)
    else:
        return error_response