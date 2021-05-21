# flask_api/db_models.py
import datetime
import uuid

from sqlalchemy.dialects.postgresql import UUID

from db import db


class User(db.Model):
    """Таблица пользователей"""
    __tablename__ = 'users'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    login = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f'<User {self.login}>'

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


class UserSignIn(db.Model):
    __tablename__ = 'users_sign_in'
    __table_args__ = {
        'postgresql_partition_by': 'LIST (user_device_type)',
        'listeners': [('after_create', create_partition)],
    }

    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))
    logined_by = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    user_agent = db.Column(db.Text)
    user_device_type = db.Column(db.Text)

    def __repr__(self):
        return f'<UserSignIn {self.user_id}:{self.logined_by}>' 