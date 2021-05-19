from typing import List, Dict, Optional
import abc
from elasticsearch import AsyncElasticsearch, exceptions

from storage.base import BaseStorage

import backoff

import logging


class FilmBaseStorage(BaseStorage):
    @abc.abstractmethod
    async def get_multi(
        self, page: int, size: int, q: str = None, order: str = None, genre: str = None
    ) -> List[Optional[Dict]]:
        pass

    @abc.abstractmethod
    async def get(self, id: str) -> Optional[Dict]:
        pass

    @abc.abstractmethod
    async def get_with_list_id(
        self, film_ids: List[str], page: int, size: int
    ) -> List[Optional[Dict]]:
        pass


class FilmElasticStorage(FilmBaseStorage):
    def __init__(self, elastic: AsyncElasticsearch):
        self.elastic = elastic

    @backoff.on_exception(backoff.expo, Exception)
    async def get_multi(
        self, page: int, size: int, q: str = None, order: str = None, genre: str = None
    ) -> List[Optional[Dict]]:

        query = {"size": size, "from": (page - 1) * size}

        if order:
            query["sort"] = {"imdb_rating": {"order": order}}

        if genre:
            query["query"] = {
                "bool": {
                    "filter": {
                        "bool": {"should": {"match_phrase": {"genres.id": genre}}}
                    }
                }
            }

        if q:
            _query = query.setdefault("query", dict())
            _bool = _query.setdefault("bool", dict())
            _bool["must"] = {
                "multi_match": {
                    "type": "best_fields",
                    "query": q,
                    "fuzziness": "auto",
                    "fields": [
                        "title^5",
                        "description^4",
                        "genres_names^3",
                        "actors_names^3",
                        "writers_names^2",
                        "directors_names^1",
                    ],
                }
            }
            _query["bool"] = _bool
            query["query"] = _query

        try:
            logging.info(query)
            doc = await self.elastic.search(index="movies", body=query)
        except exceptions.NotFoundError:
            logging.error("index not found")
            return []

        if not doc:
            return []
        result = doc["hits"]["hits"]

        if not result:
            return []

        return [film["_source"] for film in result]

    @backoff.on_exception(backoff.expo, Exception)
    async def get(self, id: str) -> Optional[Dict]:
        try:
            result = await self.elastic.get("movies", id)
            return result["_source"]

        except exceptions.NotFoundError:
            return None

    async def get_with_list_id(
        self, film_ids: List[str], page: int, size: int
    ) -> List[Optional[Dict]]:
        query = {
            "size": size,
            "from": (page - 1) * size,
            "query": {
                "bool": {
                    "should": [
                        {"match_phrase": {"id": film_id}} for film_id in film_ids
                    ],
                    "minimum_should_match": 1,
                }
            },
        }

        try:
            doc = await self.elastic.search(index="movies", body=query)
        except exceptions.NotFoundError:
            logging.error("index not found")
            return []

        if not doc:
            return []
        result = doc["hits"]["hits"]

        if not result:
            return []
        return [film["_source"] for film in result]
