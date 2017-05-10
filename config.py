import os
basedir = os.path.abspath(os.path.dirname(__file__))

# Flask-WTF flag for CSRF
CSRF_ENABLED = True

# Your App secret key
SECRET_KEY = 'gJ31x7gV26khYVO5'

# The SQLAlchemy connection string.
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
SQLALCHEMY_TRACK_MODIFICATIONS = True

# email server
MAIL_SERVER = 'smtp.gmail.com'
MAIL_USE_TLS = True
MAIL_USERNAME = 'baby.brackets@gmail.com'
MAIL_PASSWORD = 'fuckitletsdoitlive'# os.environ.get('MAIL_PASSWORD')
MAIL_DEFAULT_SENDER = 'baby.brackets@gmail.com'
