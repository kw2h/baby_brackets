from app import db
from app import app
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey


class User(db.Model):
    id = Column(Integer, primary_key=True)
    user_name = Column(String(64), index=True, unique=True, nullable=False)
    pw_hash = Column(String(120), nullable=False)
    first_name = Column(String(64))
    last_name = Column(String(64))
    email = Column(String(120), index=True, unique=True, nullable=False)
    role_id = Column(String(64), nullable=False)
    login_ct = Column(Integer)
    created = Column(DateTime)
    last_seen = Column(DateTime)
    parent_brackets = db.relationship('Bracket', foreign_keys='Bracket.parent_id', backref='parent', lazy='dynamic')
    user_brackets = db.relationship('Bracket', foreign_keys='Bracket.user_id', backref='user', lazy='dynamic')

    def __init__(self, user_name, password, first_name,
                 last_name, email, role_id, created):
        self.user_name = user_name
        self.set_password(password)
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.role_id = role_id
        self.created = created

    def set_password(self, password):
        self.pw_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.pw_hash, password)

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return unicode(self.id)  # python 2
        except NameError:
            return str(self.id)  # python 3

    def __repr__(self):
        return str(self.user_name)

class Bracket(db.Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(96))
    parent_id = Column(Integer, ForeignKey('user.id'))
    user_id = Column(Integer, ForeignKey('user.id'))
    matchups = db.relationship('Matchups', backref='bracket', lazy='dynamic')

    def __repr__(self):
        return str(self.id)

class Names(db.Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(96), nullable=False)
    seed = Column(Integer)
    matchup1 = db.relationship('Matchups', foreign_keys='Matchups.name1_id', backref='name1', lazy='dynamic')
    matchup2 = db.relationship('Matchups', foreign_keys='Matchups.name2_id', backref='name2', lazy='dynamic')
    winner = db.relationship('Matchups', foreign_keys='Matchups.winner_id', backref='winner', lazy='dynamic')

    def __repr__(self):
        return self.name

class Matchups(db.Model):
    bracket_id = Column(Integer, ForeignKey('bracket.id'), primary_key=True)
    match_id = Column(Integer, primary_key=True)
    name1_id = Column(Integer, ForeignKey('names.id'))
    name2_id = Column(Integer, ForeignKey('names.id'))
    region = Column(String(64), nullable=False)
    rnd = Column(Integer)
    winner_id = Column(Integer, ForeignKey('names.id'))

    def __repr__(self):
        return self.match_id
