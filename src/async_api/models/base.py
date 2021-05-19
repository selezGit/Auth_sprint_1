

from uuid import uuid4

import orjson
from pydantic.main import BaseModel
from pydantic.types import UUID4


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class Config:
    json_loads = orjson.loads
    json_dumps = orjson_dumps


class Base(BaseModel, Config):
    id: UUID4 = uuid4()
