from dotenv import load_dotenv
from fastapi import Request
from fastapi.templating import Jinja2Templates
from os import getenv
from typing import Any

from app.config import Settings

load_dotenv(getenv("ENV_FILE"))

settings = Settings()


def flash(request: Request, message: Any, category: str = "primary") -> None:
    if "_messages" not in request.session:
        request.session["_messages"] = []
        request.session["_messages"].append({"message": message, "category": category})


def get_flashed_messages(request: Request):
    print(request.session)
    return request.session.pop("_messages") if "_messages" in request.session else []

templates = Jinja2Templates(directory="templates")
templates.env.globals["get_flashed_messages"] = get_flashed_messages