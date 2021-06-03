from typing import Dict

import bcrypt
from sqlalchemy.orm import Session

from crud.base import CRUDBase
from db.db_models import User


class CRUDUser(CRUDBase):
    def __init__(self):
        self.model = User

    def check_password(self, user: User, password: str):
        return bcrypt.checkpw(user.password_hash.encode(), password.encode())

    def get_by(self, db: Session, **kwargs):
        return db.query(User).filter_by(**kwargs).first()

    def create(self, db: Session, *, obj_in: Dict) -> User:
        password = obj_in.pop('password')

        hash_bytes = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        password_hash = hash_bytes.decode('utf-8')
        db_obj = self.model(**obj_in)
        db_obj.password_hash = password_hash
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


user = CRUDUser()
