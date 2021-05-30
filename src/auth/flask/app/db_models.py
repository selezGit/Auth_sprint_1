import datetime
import uuid

from sqlalchemy import (Column, DateTime, ForeignKey, String, Text,
                        create_engine)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .db import Base


def create_partition(target, connection, **kw) -> None:
    """ creating partition by user_sign_in """
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "user_sign_in_smart" PARTITION OF "users_sign_in" FOR VALUES IN ('smart')"""
    )
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "user_sign_in_mobile" PARTITION OF "users_sign_in" FOR VALUES IN ('mobile')"""
    )
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "user_sign_in_web" PARTITION OF "users_sign_in" FOR VALUES IN ('web')"""
    )


class UserSignIn(Base):
    __tablename__ = 'users_sign_in'
    __table_args__ = {
        'postgresql_partition_by': 'LIST (user_device_type)',
        'listeners': [('after_create', create_partition)],
    }
    user_id = Column(UUID(as_uuid=True), ForeignKey(
        "users.id"), primary_key=True)
    logined_by = Column(DateTime, default=datetime.datetime.utcnow)
    user_agent = Column(Text)
    user_device_type = Column(Text(), nullable=True, primary_key=True)

    user = relationship("User")

    def __repr__(self):
        return f'<UserSignIn {self.user_id}:{self.logined_by}>'


class User(Base):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True,
                default=uuid.uuid4, unique=True, nullable=False)
    login = Column(String(30), unique=True, nullable=False)
    password = Column(String, nullable=False)
    email = Column(String, nullable=False)
    firstname = Column(String(255), nullable=True)

    users_sign_in = relationship('UserSignIn')

    def __init__(self, login, password):
        self.login = login
        self.password = password

    def __repr__(self):
        return f'<User {self.login}>'