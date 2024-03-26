import datetime
from sqlmodel import Field, Relationship, SQLModel
from typing import Optional


class UserBase(SQLModel):
    user_name: str = Field(index=True, unique=True, nullable=False)
    first_name: str | None = None
    last_name: str | None = None
    email: str = Field(index=True, unique=True, nullable=False)
    role_id: str = Field(nullable=False)
    login_ct: int = 0
    created: datetime.datetime = datetime.datetime.now()
    last_seen: datetime.datetime = datetime.datetime.now()


class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    pw_hash: str = Field(nullable=False)
    brackets: list["Bracket"] = Relationship(back_populates="user")
    parent_brackets: list["ParentBracket"] = Relationship(back_populates="parent")


class BracketBase(SQLModel):
    name: str = Field(nullable=False)
    completed: bool = Field(default=False)


class ParentBracket(BracketBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    parent_id: int | None = Field(default=None, foreign_key="user.id")
    parent: User | None = Relationship(back_populates="parent_brackets")
    pool: list["Bracket"] | None = Relationship(back_populates="parent_bracket")
    matchups: list["Matchup"] | None = Relationship(back_populates="parent_bracket")


class Bracket(BracketBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int | None = Field(default=None, foreign_key="user.id")
    parent_bracket_id: int | None = Field(default=None, foreign_key="parentbracket.id")
    user: User | None = Relationship(back_populates="brackets")
    parent_bracket: ParentBracket | None = Relationship(back_populates="pool")
    matchups: list["Matchup"] | None = Relationship(back_populates="bracket")


class NameMatchupLink(SQLModel, table=True):
    name_id: int | None = Field(default=None, foreign_key="name.id", primary_key=True)
    match_id: int | None = Field(default=None, foreign_key="matchup.id", primary_key=True)
    is_winner: bool = False
    name: "Name" = Relationship(back_populates="matchup_links")
    matchup: "Matchup" = Relationship(back_populates="name_links")


class MatchupBase(SQLModel):
    bracket_id: int | None = Field(default=None, foreign_key="bracket.id")
    parent_bracket_id: int | None = Field(default=None, foreign_key="parentbracket.id")
    parent_matchup_id: int | None = Field(default=None, foreign_key="matchup.id")
    region: str = Field(nullable=False)
    rnd: int = Field(nullable=False)


class Matchup(MatchupBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
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


class Name(NameBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    matchup_links: list["NameMatchupLink"] = Relationship(back_populates="name")
