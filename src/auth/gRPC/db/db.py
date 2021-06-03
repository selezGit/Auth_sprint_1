import os

import redis
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from core.config import settings
# вы можете указать свою базу, для этого нужно в переменную PG_CONNECT
# сохранить строчку в формате: 'postgresql://<username>:<password>@<host>:<port>/<database_name>'

engine = create_engine(settings.PG_CONNECT)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


redis_db = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)


def init_db():
    from . import db_models
    Base.metadata.create_all(bind=engine)


