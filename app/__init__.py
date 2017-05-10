import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_admin import Admin
from hashids import Hashids
import warnings
from flask.exthook import ExtDeprecationWarning
from config import basedir, MAIL_SERVER, MAIL_USERNAME, MAIL_PASSWORD

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
admin = Admin(app, name='User Administration', template_mode='bootstrap3')
lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'
mail = Mail(app)
bootstrap = Bootstrap(app)
hashids = Hashids(salt="gb1BDBxRVtqgsG9O")
warnings.simplefilter('ignore', ExtDeprecationWarning)

def hashidEncode(x):
    return hashids.encode(x)

app.jinja_env.globals.update(hashidEncode=hashidEncode)

from app import views, models
