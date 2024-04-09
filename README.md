# Baby Brackets

## Alembic Initialization
Initialize Alembic
```bash
alembic init -t async migrations
```
In `migrations/eny.py`, add table formatting as outlined [here](https://alembic.sqlalchemy.org/en/latest/naming.html)
```python
target_metadata.naming_convention = {
   "ix": "ix_%(column_0_label)s",
   "uq": "uq_%(table_name)s_%(column_0_name)s",
   "ck": "ck_%(table_name)s_%(constraint_name)s",
   "fk": "fk_%(table_name)s_%(column_0_name)"
         "s_%(referred_table_name)s",
   "pk": "pk_%(table_name)s"
}
```
And import out models to enable autogeneration.
```python
from app.models import (User, ParentBracket, Bracket, NameMatchupLink Matchup, Name)  # noqa: 'autogenerate' support
```
Add code to exclude certain tables (like those created by celery)
```python
exclude_tables = loads(os.getenv("DB_EXCLUDE_TABLES"))


def filter_db_objects(
       object,  # noqa: indirect usage
       name,
       type_,
       *args,  # noqa: indirect usage
       **kwargs  # noqa: indirect usage
):
   if type_ == "table":
       return name not in exclude_tables

   if type_ == "index" and name.startswith("idx") and name.endswith("geom"):
       return False

   return True


def run_migrations_offline():
   url = os.getenv("DB_ASYNC_CONNECTION_STR")
   context.configure(
       url=url,
       target_metadata=target_metadata,
       literal_binds=True,
       dialect_opts={"paramstyle": "named"},
       include_object=filter_db_objects
   )

   with context.begin_transaction():
       context.run_migrations()


def do_run_migrations(connection):
   context.configure(connection=connection, target_metadata=target_metadata)

   with context.begin_transaction():
       context.configure(
           connection=connection,
           target_metadata=target_metadata,
           include_object=filter_db_objects
       )
       context.run_migrations()


async def run_migrations_online():
   config_section = config.get_section(config.config_ini_section)
   url = os.getenv("DB_ASYNC_CONNECTION_STR")
   config_section["sqlalchemy.url"] = url

   connectable = AsyncEngine(
       engine_from_config(
           config_section,
           prefix="sqlalchemy.",
           poolclass=pool.NullPool,
           future=True,
       )
   )

   async with connectable.connect() as connection:
       await connection.run_sync(do_run_migrations)

   await connectable.dispose()


if context.is_offline_mode():
   run_migrations_offline()
else:
   asyncio.run(run_migrations_online())
```
Ensure the sqlmodel library is imported in migrations scripts by editing
`migrations/script.py.mako` to include `import sqlmodel`
```
...
import sqlmodel
“${imports if imports else “”}
...
```
Auto-generate scripts and upgrade the DB
```bash
alembic revision --autogenerate -m "User" -m "ParentBracket" -m "Bracket" -m "NameMatchupLink" -m "Matchup" -m "Name"
alembic upgrade head 
```