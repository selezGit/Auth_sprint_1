from pydantic import BaseSettings, Field


class Config(BaseSettings):
    # вы можете указать свою базу, для этого нужно в переменную PG_CONNECT
    # сохранить строчку в формате: 'postgresql://<username>:<password>@<host>:<port>/<database_name>'
    PG_CONNECT: str = Field(
        "postgresql://auth_admin:1234@db-auth/auth", env='PG_CONNECT')
    REDIS_HOST: str = Field("redis-auth", env='REDIS_HOST')
    REDIS_PORT: int = Field(6379, env='REDIS_PORT')
    SECRET_KEY: str = Field("somesecret", env='SECRET_KEY')


settings = Config()
