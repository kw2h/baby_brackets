from fastapi import APIRouter, Request, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app import templates
from app.database import get_async_session
from app.auth import  get_session_token_from_cookie

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
    except:
        session_token = None
    return templates.TemplateResponse(
        "pages/index.html",
        context={
            "request": request,
            "session_token": session_token
        }
    )
