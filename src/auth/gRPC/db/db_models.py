import datetime
import os
import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .db import Base

SECRET_KEY = os.getenv('SECRET_KEY', 'somesecret')


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
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey(
        "users.id"), primary_key=True)
    logined_by = Column(DateTime, default=datetime.utcnow)
    user_agent = Column(Text)
    user_device_type = Column(String, primary_key=True)

    active = Column(Boolean, default=True)
    user = relationship("User")

    def __repr__(self):
        return f'<UserSignIn {self.user_id}:{self.logined_by}>'


class User(Base):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    login = Column(String(30), unique=True, nullable=False)
    password_hash = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    admin = Column(Boolean, default=False)

    users_sign_in = relationship('UserSignIn', cascade="all,delete")

    def __repr__(self):
        return f'<User {self.login}, ID: {self.id}, admin={self.admin}>'

    def __init__(self, login: str = None, password_hash: str = None, email: str = None, admin: bool = False):
        self.login = login
        self.password_hash = password_hash
        self.email = email
        self.admin = admin
