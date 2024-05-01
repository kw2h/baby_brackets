from fastapi import Depends, HTTPException, Request
import json
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.crudrouter import SQLAlchemyCRUDRouter
from app.database import get_async_session
from app.auth import get_password_hash, get_current_user_for_api
from app.models import (User, UserUpdate, UserCreate, UserReadWithBrackets, 
                        ParentBracket, ParentBracketUpdate, Bracket, BracketUpdate,
                        Matchup, Name, NameMatchupLink)


user_router = SQLAlchemyCRUDRouter(
    schema=User,
    create_schema=UserCreate,
    update_schema=UserUpdate,
    db_model=User,
    db=get_async_session,
    prefix=User.__tablename__,
    get_all_route=False,
    get_one_route=True,
    delete_one_route=True,
    create_route=False,
    update_route=True,
    get_one_resp_model=UserReadWithBrackets
)

# @user_router.get("/{item_id}", response_model=UserReadWithBrackets)
# async def get_one(*, 
#     item_id: str,
#     db: AsyncSession = Depends(get_async_session)  # type: ignore
# ) -> UserReadWithBrackets:
#     user: User = await db.get_one(User, item_id)
#     # await db.refresh(user, ["brackets", "parent_brackets"])
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
#     else:
#         return user


@user_router.post("")
async def create_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_async_session),
) -> User:
    try:
        extra_data = {"pw_hash": get_password_hash(user.password)}
        db_user = User.model_validate(user, update=extra_data)
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user
    except IntegrityError:
        await db.rollback()
        raise HTTPException(422, "Integrity Error") from None


parentbracket_router = SQLAlchemyCRUDRouter(
    schema=ParentBracket,
    # create_schema=None,
    update_schema=ParentBracketUpdate,
    db_model=ParentBracket,
    db=get_async_session,
    prefix=ParentBracket.__tablename__,
    get_all_route=False,
    get_one_route=True,
    delete_one_route=True,
    create_route=True,
    update_route=True,
    dependencies=[Depends(get_current_user_for_api)],
)


bracket_router = SQLAlchemyCRUDRouter(
    schema=Bracket,
    # create_schema=None,
    update_schema=BracketUpdate,
    db_model=Bracket,
    db=get_async_session,
    prefix=Bracket.__tablename__,
    get_all_route=False,
    get_one_route=True,
    delete_one_route=True,
    create_route=True,
    update_route=True,
    dependencies=[Depends(get_current_user_for_api)],
)


matchup_router = SQLAlchemyCRUDRouter(
    schema=Matchup,
    # create_schema=None,
    # update_schema=None,
    db_model=Matchup,
    db=get_async_session,
    prefix=Matchup.__tablename__,
    get_all_route=False,
    get_one_route=True,
    delete_one_route=True,
    create_route=True,
    update_route=True,
    dependencies=[Depends(get_current_user_for_api)],
)


name_router = SQLAlchemyCRUDRouter(
    schema=Name,
    # create_schema=None,
    # update_schema=None,
    db_model=Name,
    db=get_async_session,
    prefix=Name.__tablename__,
    get_all_route=False,
    get_one_route=True,
    delete_one_route=True,
    create_route=True,
    update_route=False,
    dependencies=[Depends(get_current_user_for_api)],
)


namemtchuplink_router = SQLAlchemyCRUDRouter(
    schema=NameMatchupLink,
    # create_schema=None,
    # update_schema=None,
    db_model=NameMatchupLink,
    db=get_async_session,
    prefix=NameMatchupLink.__tablename__,
    get_all_route=False,
    get_one_route=True,
    delete_one_route=True,
    create_route=True,
    update_route=True,
    dependencies=[Depends(get_current_user_for_api)],
)