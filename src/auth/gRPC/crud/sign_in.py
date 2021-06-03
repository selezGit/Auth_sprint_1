from crud.base import CRUDBase
from db.db_models import UserSignIn


class CRUDSignIn(CRUDBase):
    def __init__(self):
        self.model = UserSignIn


sign_in = CRUDSignIn()
