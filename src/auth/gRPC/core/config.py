from pydantic import BaseSettings


class Config(BaseSettings):
    PG_CONNECT: str = "postgresql://auth_admin:1234@db-auth/auth"
    REDIS_HOST = "redis-auth"
    REDIS_PORT = 6380
    SECRET_KEY = "somesecret"
settings = Config()
