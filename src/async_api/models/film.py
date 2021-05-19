
from datetime import datetime
from typing import List, Optional

from models.base import Base
from models.genre import Genre


class Person(Base):
    name: str


class Film(Base):
    title: str
    description: Optional[str] = ''
    imdb_rating: Optional[float] = 0
    creation_date: datetime = datetime.now()
    restriction: Optional[int] = 0
    directors: List[Person] = []
    actors: List[Person] = []
    writers: List[Person] = []
    genres: List[Genre] = []
    file_path: Optional[str] = ''


class FilmShort(Base):
    title: str
    imdb_rating: Optional[float] = 0
