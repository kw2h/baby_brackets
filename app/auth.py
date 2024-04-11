from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status, Request
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.security import OAuth2, OAuth2PasswordBearer
from fastapi.security.utils import get_authorization_scheme_param
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Annotated, Optional, Dict

from app import settings
from app.database import get_async_session
from app.models import User, TokenData, SessionToken


class OAuth2PasswordBearerWithCookie(OAuth2):
    """
    This class is taken directly from FastAPI:
    https://github.com/tiangolo/fastapi/blob/26f725d259c5dbe3654f221e608b14412c6b40da/fastapi/security/oauth2.py#L140-L171
    
    The only change made is that authentication is taken from a cookie instead of from the header
    """
    def __init__(
        self,
        tokenUrl: str,
        scheme_name: Optional[str] = None,
        scopes: Optional[Dict[str, str]] = None,
        description: Optional[str] = None,
        auto_error: bool = True,
    ):
        if not scopes:
            scopes = {}
        flows = OAuthFlowsModel(password={"tokenUrl": tokenUrl, "scopes": scopes})
        super().__init__(
            flows=flows,
            scheme_name=scheme_name,
            description=description,
            auto_error=auto_error,
        )

    async def __call__(self, request: Request) -> Optional[str]:
        # `request.cookies.get(settings.COOKIE_NAME)` instead of 
        # `request.headers.get("Authorization")`
        authorization: str = request.cookies.get(settings.cookie_name) 
        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                return None
        return param


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer_scheme = OAuth2PasswordBearer(tokenUrl="token_bearer")
oauth2_cookie_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="token_cookie")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


async def get_user(username: str, db: AsyncSession) -> User:
    stmt = select(User).where(User.username == username)
    result = await db.exec(stmt)
    user = result.first()
    return user


async def get_session(session_id: str, db: AsyncSession) -> SessionToken:
    stmt = select(SessionToken).where(SessionToken.session_id == session_id)
    result = await db.exec(stmt)
    session_token = result.first()
    return session_token


async def authenticate_user(username: str, password: str, db: AsyncSession) -> User:
    user = await get_user(username, db)
    if not user:
        return False
    if not verify_password(password, user.pw_hash): 
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


# async def decode_token(token: str, db: AsyncSession = Depends(get_async_session)) -> User:
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED, 
#         detail="Could not validate credentials."
#     )
#     token = token.removeprefix("Bearer").strip()
#     try:
#         payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
#         username: str = payload.get("username")
#         if username is None:
#             raise credentials_exception
#     except JWTError as e:
#         print(e)
#         raise credentials_exception
    
#     user = await get_user(username, db=db)
#     return user


async def decode_session(token: str, db: AsyncSession = Depends(get_async_session)) -> SessionToken:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, 
        detail="Could not validate credentials."
    )
    token = token.removeprefix("Bearer").strip()
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        session_id: str = payload.get("session_id")
        if session_id is None:
            raise credentials_exception
    except JWTError as e:
        print(e)
        raise credentials_exception
    
    session_token = await get_session(session_id, db=db)
    return session_token


async def get_current_user_for_api(
    token: Annotated[str, Depends(oauth2_bearer_scheme)],
    db: AsyncSession = Depends(get_async_session)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(username=token_data.username, db=db)
    if user is None:
        raise credentials_exception
    return user


# async def get_current_user_from_token(
#     token: str = Depends(oauth2_cookie_scheme),
#     db: AsyncSession = Depends(get_async_session)
# ) -> User:
#     """
#     Get the current user from the cookies in a request.

#     Use this function when you want to lock down a route so that only decode_token
#     authenticated users can see access the route.
#     """
#     user = await decode_token(token, db)
#     return user


async def get_session_from_token(
    token: str = Depends(oauth2_cookie_scheme),
    db: AsyncSession = Depends(get_async_session)
) -> User:
    """
    Get the SessionToken from the cookies in a request.

    Use this function when you want to lock down a route so that only decode_token
    authenticated users can see access the route.
    """
    session_token = await decode_session(token, db)
    return session_token


# async def get_current_user_from_cookie(
#     request: Request,
#     db: AsyncSession = Depends(get_async_session)
# ) -> User:
#     """
#     Get the current user from the cookies in a request.
    
#     Use this function from inside other routes to get the current user. Good
#     for views that should work for both logged in, and not logged in users.
#     """
#     token = request.cookies.get(settings.cookie_name)
#     user = await decode_token(token, db)
#     return user


async def get_session_token_from_cookie(
    request: Request,
    db: AsyncSession = Depends(get_async_session)
) -> SessionToken:
    """
    Get the SessionToken from the cookies in a request.
    
    Use this function from inside other routes to get the current user. Good
    for views that should work for both logged in, and not logged in users.
    """
    token = request.cookies.get(settings.cookie_name)
    session_token = await decode_session(token, db)
    return session_token