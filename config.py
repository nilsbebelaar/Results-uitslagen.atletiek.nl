from environs import Env
env = Env()


ALLOWED_DOMAINS = ['uitslagen.atletiek.nl',
                   'ergebnisse.leichtathletik.de',
                   'laportal.net',
                   'slv.laportal.net',
                   'fla.laportal.net']


class Config:
    """Set Flask config variables."""

    FLASK_APP = 'start.py'
    FLASK_DEBUG = True
    TESTING = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///../database/uitslagen.sqlite'

    STATIC_FOLDER = 'static'
    TEMPLATES_FOLDER = 'templates'

    PROXY_DOMAIN = env('PROXY_DOMAIN')
    PROXY_PORT = env('PROXY_PORT')
    PROXY_USER = env('PROXY_USER')
    PROXY_PASS = env('PROXY_PASS')

    import secrets
    SECRET_KEY = secrets.token_hex(64)
