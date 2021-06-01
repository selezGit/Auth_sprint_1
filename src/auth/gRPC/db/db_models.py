import datetime
import os
import uuid
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from db.no_sql_db import add_refresh_token, add_to_blacklist, del_refresh_token

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
    user_id = Column(UUID(as_uuid=True), ForeignKey(
        "users.id"), primary_key=True)
    logined_by = Column(DateTime, default=datetime.utcnow)
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
    password_hash = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False)
    admin = Column(Boolean, default=False)

    users_sign_in = relationship('UserSignIn')

    def __init__(self, login, password):
        self.login = login
        self.password = password

    def __repr__(self):
        return f'<User {self.login}, ID: {self.id}, admin={self.admin}>'

    @property
    def password(self):
        raise AttributeError("password: write-only field")

    @password.setter
    def set_password(self, password):
        hash_bytes = bcrypt.hashpw(password, bcrypt.gensalt())
        self.password_hash = hash_bytes.decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(self.password_hash, password)

    @classmethod
    def find_by_email(cls, email):
        return cls.query.filter_by(email=email).first()

    def _create_access_token(self) -> bytes:
        """Функция создаёт access jwt токен"""
        now = datetime.now(timezone.utc)
        expire = now + timedelta(minutes=15)
        payload = dict(exp=expire, iat=now, sub=self.id, admin=self.admin)
        access_token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        return access_token

    def _create_refresh_token(self) -> bytes:
        """Функция создаёт refresh jwt токен"""
        now = datetime.now(timezone.utc)
        expire = now + timedelta(days=7)
        payload = dict(exp=expire, iat=now, sub=self.id)
        refresh_token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        add_refresh_token(refresh_token)
        return refresh_token
