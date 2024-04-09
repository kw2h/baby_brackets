from fastapi import APIRouter, Request, Depends

from app import templates, settings
from app.auth import  get_current_user_from_cookie
from app.models import User

# --------------------------------------------------------------------------------
# Router
# --------------------------------------------------------------------------------

router = APIRouter()


# --------------------------------------------------------------------------------
# Routes
# --------------------------------------------------------------------------------

@router.get("/index", tags=["Pages"])
async def index(request: Request):
    try:
        user = await get_current_user_from_cookie(request)
    except:
        user = None
    print(request.cookies.get(settings.cookie_name))
    return templates.TemplateResponse(
        "pages/index.html",
        context={
            "request": request,
            "user": user
        }
    )
