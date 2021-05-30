from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from .config import DevelopmentConfig


engine = create_engine(DevelopmentConfig.PG_CONNECT)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    from . import db_models
    Base.metadata.create_all(bind=engine)
