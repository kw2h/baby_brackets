from dotenv import load_dotenv
from fastapi.templating import Jinja2Templates
from os import getenv

from app.config import Settings

load_dotenv(getenv("ENV_FILE"))

settings = Settings()

templates = Jinja2Templates(directory="templates")