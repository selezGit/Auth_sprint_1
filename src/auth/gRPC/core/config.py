from os import environ
from pydantic import BaseSettings, Field


class Config(BaseSettings):
    # вы можете указать свою базу, для этого нужно в переменную PG_CONNECT
    # сохранить строчку в формате: 'postgresql://<username>:<password>@<host>:<port>/<database_name>'
    PG_CONNECT: str = Field("postgresql://auth_admin:1234@db-auth/auth", env='PG_CONNECT')
    REDIS_HOST = "redis-auth"
    REDIS_PORT = 6380
    SECRET_KEY = "somesecret"
settings = Config()
