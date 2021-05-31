from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
import os

# вы можете указать свою базу, для этого нужно в переменную PG_CONNECT
# сохранить строчку в формате: 'postgresql://<username>:<password>@<host>:<port>/<database_name>'
PG_CONNECT = os.getenv('PG_CONNECT', 'postgresql://auth_admin:1234@db-auth/auth')


engine = create_engine(PG_CONNECT)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    from . import db_models
    Base.metadata.create_all(bind=engine)
