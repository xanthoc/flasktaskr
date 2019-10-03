import os

# grab the foler where this script lives
basedir = os.path.abspath(os.path.dirname(__file__))

DATABASE = 'flasktaskr.db'
CSRF_ENABLED = True
SECRET_KEY = 'my_precisou'
SQLALCHEMY_TRACK_MODIFICATIONS = True
DEBUG = True

#define the full path for the database
DATABASE_PATH = os.path.join(basedir, DATABASE)

# the database URI
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DATABASE_PATH