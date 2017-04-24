import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_admin import Admin
import warnings
from flask.exthook import ExtDeprecationWarning
from config import basedir, ADMINS, MAIL_SERVER, MAIL_USERNAME, MAIL_PASSWORD

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
admin = Admin(app, name='User Administration', template_mode='bootstrap3')
lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'
mail = Mail(app)
bootstrap = Bootstrap(app)
warnings.simplefilter('ignore', ExtDeprecationWarning)


from app import views, models
