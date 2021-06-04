from typing import TypeVar, Type, Any, Optional, Dict

from sqlalchemy import inspect
from sqlalchemy.orm import Session
from db.db import Base

ModelType = TypeVar("ModelType", bound=Base)


def object_as_dict(obj):
    return {c.key: getattr(obj, c.key)
            for c in inspect(obj).mapper.column_attrs}


class CRUDBase:
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        return db.query(self.model).filter(self.model.id == id).first()

    def get_by(self, db: Session, **kwargs):
        return db.query(self.model).filter_by(**kwargs).first()

    def create(self, db: Session, *, obj_in: Dict) -> ModelType:
        db_obj = self.model(**obj_in)  # type: ignore
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
            self,
            db: Session,
            *,
            db_obj: ModelType,
            obj_in: Dict[str, Any],
    ) -> ModelType:
        obj_data = object_as_dict(db_obj)
        update_data = obj_in

        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
