from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, JSONResponse

from app.auth import  get_session_from_token
from app.models import SessionToken
from app.load_names import load_names, prefix_search, random_name


NAMES_DF = load_names("namesbystate.zip")


# --------------------------------------------------------------------------------
# Router
# --------------------------------------------------------------------------------

router = APIRouter()


# --------------------------------------------------------------------------------
# Routes
# --------------------------------------------------------------------------------


@router.get("/searchname", response_class=HTMLResponse)
def search(
    request: Request,
    session_token: SessionToken = Depends(get_session_from_token),
):
    """ Not validating the params as the name attribute is used by htmx
    to pass request query params, but that needs to match the form name
    in order to be submitted properly when the post request is sent.
    """
    if not session_token:
        return "Unauthorized", 404
    query = next(iter(request.query_params.values()))
    names = prefix_search(NAMES_DF, query, None)
    response = ""
    for d in names:
        name = d.get("name")
        response += f'<option value={name}>{name}</option>'
    return response


@router.get("/randomname/{sex}", response_class=JSONResponse)
def search(
    sex: str | None = None,
    session_token: SessionToken = Depends(get_session_from_token)
):
    if not session_token:
        return "Unauthorized", 404
    name = random_name(NAMES_DF, sex)
    return name