from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
matchups = Table('matchups', post_meta,
    Column('bracket_id', Integer, primary_key=True, nullable=False),
    Column('match_id', Integer, primary_key=True, nullable=False),
    Column('name1_id', Integer),
    Column('name2_id', Integer),
    Column('region', String(length=64), nullable=False),
    Column('rnd', Integer),
    Column('winner_id', Integer),
    Column('scoring_bracket_id', Integer),
    Column('scoring_match_id', Integer),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['matchups'].columns['scoring_bracket_id'].create()
    post_meta.tables['matchups'].columns['scoring_match_id'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['matchups'].columns['scoring_bracket_id'].drop()
    post_meta.tables['matchups'].columns['scoring_match_id'].drop()
