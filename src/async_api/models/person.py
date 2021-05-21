from typing import List, Optional

from pydantic import UUID4

from models.base import Base


class Person(Base):
    full_name: str
    role: List[str]
    film_ids: Optional[List[UUID4]]
