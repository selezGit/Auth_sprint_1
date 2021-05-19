import abc
import logging
from typing import Dict, List, Optional

import backoff
from elasticsearch import AsyncElasticsearch, exceptions

from storage.base import BaseStorage


class GenreBaseStorage(BaseStorage):
    @abc.abstractmethod
    async def get_multi(
            self, page: int, size: int) -> List[Optional[Dict]]:
        pass

    @abc.abstractmethod
    async def get(self, id: str) -> Optional[Dict]:
        pass


class GenreElasticStorage(GenreBaseStorage):
    def __init__(self, elastic: AsyncElasticsearch):
        self.elastic = elastic

    @backoff.on_exception(backoff.expo, Exception)
    async def get(self, id: str) -> Optional[Dict]:
        try:
            result = await self.elastic.get('genre', id)
            return result['_source']

        except exceptions.NotFoundError:
            return None

    @backoff.on_exception(backoff.expo, Exception)
    async def get_multi(
            self, page: int, size: int) -> List[Optional[Dict]]:
        try:
            if page:
                query = {'size': size, 'from': (page - 1) * size}
            doc = await self.elastic.search(index='genre', body=query)
        except exceptions.NotFoundError:
            logging.info('index not found')
            return []

        if not doc:
            return []
        result = doc['hits']['hits']

        if not result:
            return []

        return [genre['_source'] for genre in result]
