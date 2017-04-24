from app import db
from app import app
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship


class User(db.Model):
    id = Column(Integer, primary_key=True)
    user_name = Column(String(64), index=True, unique=True, nullable=False)
    pw_hash = Column(String(120), nullable=False)
    first_name = Column(String(64))
    last_name = Column(String(64))
    email = Column(String(120), index=True, unique=True, nullable=False)
    role_id = Column(Integer, ForeignKey('role.id'), nullable=False)
    login_ct = Column(Integer)
    created = Column(DateTime)
    last_seen = Column(DateTime)
    role = relationship("Role", foreign_keys=[role_id])

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

class Role(db.Model):
    id = Column(Integer, primary_key=True)
    role_name = Column(String(96))

    def __repr__(self):
        return str(self.role_name)

class BabyBracket(db.Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(96))
    owner_id = Column(Integer, ForeignKey('user.id'))
    parent_id = Column(Integer, ForeignKey('user.id'))
    owner = relationship("User", foreign_keys=[owner_id])
    parent = relationship("User", foreign_keys=[parent_id])

    def __repr__(self):
        return str(self.id)

class Names(db.Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(96), unique = True, nullable=False)
    region = Column(String(64), unique = True, nullable=False)
    seed = Column(Integer)

    def __repr__(self):
        return self.name

class Matchups(db.Model):
    bracket = Column(Integer, ForeignKey('baby_bracket.id'), primary_key=True)
    match_id = Column(Integer, primary_key=True)
    name = Column(Integer, ForeignKey('names.id'))
    win = Column(Boolean)
    baby_bracket = relationship("BabyBracket")
    names = relationship("Names")

    def __repr__(self):
        return self.match_id
