from sqlmodel import SQLModel, create_engine


_sqlite_file_name = "database.db"
SQLALCHEMY_DATABASE_URL = f"sqlite:///{_sqlite_file_name}"
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"

connect_args = {"check_same_thread": False}
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True, connect_args=connect_args)  # only needed for SQLite
# engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)