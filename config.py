from os import path
from dotenv import load_dotenv
from environs import Env

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.env'))
env = Env()

class Config:
    """Set Flask config variables."""

    FLASK_APP = 'start.py'
    FLASK_DEBUG = env.bool('FLASK_DEBUG')
    TESTING = env.bool('FLASK_TESTING')

    STATIC_FOLDER = 'static'
    TEMPLATES_FOLDER = 'templates'

    import secrets
    SECRET_KEY = secrets.token_hex(64)


