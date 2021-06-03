from pydantic import BaseSettings


class Config(BaseSettings):
    PG_CONNECT: str = "postgresql://dbuser:admin2021@localhost:5432/todoapp"
    REDIS_HOST = "redis-auth"
    REDIS_PORT = 6380
    SECRET_KEY = "somesecret"


settings = Config()
