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

    import secrets
    SECRET_KEY = secrets.token_hex(64)
