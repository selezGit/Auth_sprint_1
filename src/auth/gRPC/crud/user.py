from typing import Dict, Any

import bcrypt
from sqlalchemy.orm import Session

from crud.base import CRUDBase
from db.db_models import User


class CRUDUser(CRUDBase):
    def __init__(self):
        self.model = User

    def check_password(self, user: User, password: str):
        return bcrypt.checkpw(password.encode(), user.password_hash.encode())

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

    def update(
            self,
            db: Session,
            *,
            db_obj: User,
            obj_in: Dict[str, Any],
    ) -> User:
        if obj_in.get('password'):
            password = obj_in.pop('password')
            hash_bytes = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
            password_hash = hash_bytes.decode('utf-8')
            obj_in['password_hash'] = password_hash
        return super().update(db=db, db_obj=db_obj, obj_in=obj_in)


user = CRUDUser()
