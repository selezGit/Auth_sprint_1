from typing import Generator

import redis
from core.config import settings
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker



engine = create_engine(settings.PG_CONNECT)
SessionLocal = sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine)
Base = declarative_base()

redis_db = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)


def init_db():
    from . import db_models
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
