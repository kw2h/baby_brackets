import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.main import app, get_session
from app.models import User, Bracket, ParentBracket, Matchup, NameMatchupLink, Name


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

def setup_users_brackets():
    # create a parent user and a regular user
    parent_user = User(
        user_name="parent_user",
        first_name="daddy",
        last_name="shark",
        email="testuser@fakemail.com",
        role_id="1",
        pw_hash="hashedpw"
    )
    test_user = User(
        user_name="test_user",
        first_name="grandpa",
        last_name="shark",
        email="PRUNES@aol.com",
        role_id="1",
        pw_hash="hashedpw"
    )

    # create a parent bracket:
    parent_bracket = ParentBracket(
        name="parent bracket",
        parent=parent_user
    )
    
    # create a user bracket:
    user_bracket = Bracket(
        name="user bracket",
        user=test_user,
        parent_bracket=parent_bracket
    )
    return {
        "parent_user": parent_user,
        "test_user": test_user,
        "parent_bracket": parent_bracket,
        "user_bracket": user_bracket,
    }


def test_user_bracket(session: Session) -> None:
    setup_dict = setup_users_brackets()
    parent_user = setup_dict["parent_user"]
    test_user = setup_dict["test_user"]
    parent_bracket = setup_dict["parent_bracket"]
    user_bracket = setup_dict["user_bracket"]

    # commit to DB:
    session.add(parent_bracket)
    session.add(user_bracket)
    session.commit()

    # Do some checks:
    assert parent_user.parent_brackets == [parent_bracket]
    assert test_user.brackets == [user_bracket]
    
    assert user_bracket.user == test_user
    assert parent_bracket.parent == parent_user
    assert parent_bracket.pool == [user_bracket]
    assert user_bracket.parent_bracket == parent_bracket


def test_name_matchup(session: Session) -> None:
    setup_dict = setup_users_brackets()
    parent_user = setup_dict["parent_user"]
    test_user = setup_dict["test_user"]
    parent_bracket = setup_dict["parent_bracket"]
    user_bracket = setup_dict["user_bracket"]

    # create a parent bracket:
    parent_bracket = ParentBracket(
        name="parent bracket",
        parent=parent_user
    )

    # create 2 matchups w/ names for the parent bracket
    # and link to parent_bracket
    names = [("Gemma", "Erin"), ("Ella", "Remy")]
    seeds = [(1,4), (2,3)]
    for region,nms,sds in zip(["east", "midwest"], names, seeds):
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
            session.add(parent_bracket_matchup_name_link)
        session.add(parent_bracket_matchup)

    # commit to DB:
    session.commit()

    assert len(parent_bracket.matchups) == 2
    assert len(parent_bracket.matchups[0].name_links) == 2
    assert len(parent_bracket.matchups[1].name_links) == 2
    assert parent_bracket.matchups[0].name_links[0].is_winner == False
    assert parent_bracket.matchups[0].name_links[1].is_winner == False
    assert parent_bracket.matchups[1].name_links[0].is_winner == False
    assert parent_bracket.matchups[1].name_links[1].is_winner == False

    # create a parent bracket:
    user_bracket = Bracket(
        name="user bracket",
        user=test_user,
        parent_bracket_id=parent_bracket.id
    )

    # copy 2 matchups from the parent_bracket
    # with bracket linked to user_bracket
    # and parent_matchup correctly set
    for m in parent_bracket.matchups:
        user_bracket_matchup = Matchup(
            parent_bracket_id=m.parent_bracket_id,
            bracket=user_bracket,
            region=m.region,
            rnd=m.rnd,
            parent_matchup_id=m.id
        )
        for n in m.name_links:
            user_bracket_matchup_name_link = NameMatchupLink(
                name=n.name,
                matchup=user_bracket_matchup
            )
            session.add(user_bracket_matchup_name_link)
    
    session.add(user_bracket)
    session.commit()

    assert len(user_bracket.matchups) == 2
    assert user_bracket.matchups[0].name_links[0].name == parent_bracket.matchups[0].name_links[0].name
    assert user_bracket.matchups[0].name_links[1].name == parent_bracket.matchups[0].name_links[1].name
    assert user_bracket.matchups[1].name_links[0].name == parent_bracket.matchups[1].name_links[0].name
    assert user_bracket.matchups[1].name_links[1].name == parent_bracket.matchups[1].name_links[1].name
    assert user_bracket.matchups[0].parent_bracket == parent_bracket
    assert user_bracket.matchups[1].parent_bracket == parent_bracket
    assert parent_bracket.pool == [user_bracket]
    assert user_bracket.matchups[0].parent_matchup == parent_bracket.matchups[0]
    assert user_bracket.matchups[1].parent_matchup == parent_bracket.matchups[1]