
from crud.base import CRUDBase
from db.db_models import UserSignIn
from sqlalchemy.orm import Session


class CRUDSignIn(CRUDBase):
    def __init__(self):
        self.model = UserSignIn

    def get_history(self, db: Session, user_id: str, skip, limit):
        return db.query(UserSignIn).filter(UserSignIn.user_id == user_id).order_by(UserSignIn.logined_by.desc()).offset(
            skip).limit(limit).all()


sign_in = CRUDSignIn()
