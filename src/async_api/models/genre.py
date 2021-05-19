from typing import Optional

from models.base import Base

class Genre(Base):
    name: str
    description: Optional[str] = ''
