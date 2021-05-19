from dataclasses import dataclass

from multidict import CIMultiDictProxy


@dataclass
class HTTPResponse:
    body: dict
    headers: CIMultiDictProxy[str]
    status: int
    url: str
    resp_speed: int
