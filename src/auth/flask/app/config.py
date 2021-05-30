import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    # вы можете указать свою базу, для этого нужно в переменную PG_CONNECT
    # сохранить строчку в формате: 'postgresql://<username>:<password>@<host>:<port>/<database_name>'
    PG_CONNECT = os.getenv(
        'PG_CONNECT', 'postgresql://auth_admin:1234@db-auth/auth')


class DevelopmentConfig(Config):
    DEBUG = True


class ProdConfig(Config):
    DBUG = False
