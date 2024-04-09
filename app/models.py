import datetime
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlmodel import Field, Relationship, SQLModel
from typing import Optional
import uuid


class HealthCheck(BaseModel):
    name: str
    version: str
    description: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class UUIDModel(SQLModel):
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False,
    )


class UserBase(SQLModel):
    username: str = Field(index=True, unique=True, nullable=False)
    first_name: str | None = None
    last_name: str | None = None
    email: str = Field(index=True, unique=True, nullable=False)
    role_id: str = Field(nullable=False)
    login_ct: int = 0
    created: datetime.datetime = datetime.datetime.now()
    last_seen: datetime.datetime = datetime.datetime.now()


class User(UUIDModel, UserBase, AsyncAttrs, table=True):
    pw_hash: str = Field(nullable=False)
    brackets: Optional[list["Bracket"]] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"lazy": "selectin"}
    )
    parent_brackets: Optional[list["ParentBracket"]] = Relationship(
        back_populates="parent",
        sa_relationship_kwargs={"lazy": "selectin"}
    )


class UserCreate(UserBase): 
    password: str


class UserRead(UUIDModel, UserBase):
    pass


class UserUpdate(UserBase): 
    pw_hash: str = Field(nullable=False)
    brackets: list["Bracket"] = Relationship(back_populates="user")
    parent_brackets: list["ParentBracket"] = Relationship(back_populates="parent")


class BracketBase(SQLModel):
    name: str = Field(nullable=False)
    completed: bool = Field(default=False)


class ParentBracket(UUIDModel, BracketBase, table=True):
    parent_id: uuid.UUID | None = Field(default=None, foreign_key="user.id")
    parent: User | None = Relationship(back_populates="parent_brackets")
    pool: list["Bracket"] | None = Relationship(back_populates="parent_bracket")
    matchups: list["Matchup"] | None = Relationship(back_populates="parent_bracket")


class ParentBracketRead(UUIDModel, BracketBase):
    parent_id: uuid.UUID


class ParentBracketUpdate(BracketBase):
    parent_id: uuid.UUID | None = Field(default=None, foreign_key="user.id")
    matchups: list["Matchup"] | None = None


class Bracket(UUIDModel, BracketBase, table=True):
    user_id: uuid.UUID | None = Field(default=None, foreign_key="user.id")
    parent_bracket_id: uuid.UUID | None = Field(default=None, foreign_key="parentbracket.id")
    user: User | None = Relationship(back_populates="brackets")
    parent_bracket: ParentBracket | None = Relationship(back_populates="pool")
    matchups: list["Matchup"] | None = Relationship(back_populates="bracket")


class BracketRead(UUIDModel, BracketBase):
    user_id: uuid.UUID
    parent_bracket_id: uuid.UUID


class BracketUpdate(BracketBase):
    user_id: uuid.UUID | None = Field(default=None, foreign_key="user.id")
    matchups: list["Matchup"] | None = None


class NameMatchupLink(SQLModel, table=True):
    name_id: uuid.UUID | None = Field(default=None, foreign_key="name.id", primary_key=True)
    match_id: uuid.UUID | None = Field(default=None, foreign_key="matchup.id", primary_key=True)
    is_winner: bool = False
    name: "Name" = Relationship(back_populates="matchup_links")
    matchup: "Matchup" = Relationship(back_populates="name_links")


class MatchupBase(SQLModel):
    bracket_id: uuid.UUID | None = Field(default=None, foreign_key="bracket.id")
    parent_bracket_id: uuid.UUID | None = Field(default=None, foreign_key="parentbracket.id")
    parent_matchup_id: uuid.UUID | None = Field(default=None, foreign_key="matchup.id")
    region: str = Field(nullable=False)
    rnd: int = Field(nullable=False)


class Matchup(UUIDModel, MatchupBase, table=True):
    bracket: Bracket | None = Relationship(back_populates="matchups")
    parent_bracket: ParentBracket | None = Relationship(back_populates="matchups")
    name_links: list["NameMatchupLink"] = Relationship(back_populates="matchup")
    # https://stackoverflow.com/questions/73420018/how-do-i-construct-a-self-referential-recursive-sqlmodel
    parent_matchup: Optional["Matchup"] = Relationship(
        back_populates="pool_matchups",
        sa_relationship_kwargs={"remote_side": "Matchup.id"}
    )
    pool_matchups: list["Matchup"] | None = Relationship(back_populates="parent_matchup")


class NameBase(SQLModel):
    name: str = Field(nullable=False)
    seed: int = Field(nullable=False)


class Name(UUIDModel, NameBase, table=True):
    matchup_links: list["NameMatchupLink"] = Relationship(back_populates="name")


class UserReadWithBrackets(UserRead):
    brackets: list[BracketRead] = []
    parent_brackets: list[ParentBracketRead] = []