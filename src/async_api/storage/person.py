import abc
import logging
from typing import Dict, List, Optional

import backoff
from elasticsearch import AsyncElasticsearch, exceptions

from storage.base import BaseStorage


class PersonBaseStorage(BaseStorage):
    @abc.abstractmethod
    async def get_multi(
            self, page: int, size: int, q: str = None) -> List[Optional[Dict]]:
        pass

    @abc.abstractmethod
    async def get(self, id: str) -> Optional[Dict]:
        pass


class PersonElasticStorage(PersonBaseStorage):
    def __init__(self, elastic: AsyncElasticsearch):
        self.elastic = elastic

    @backoff.on_exception(backoff.expo, Exception)
    async def get(self, id: str) -> Optional[Dict]:
        try:
            result = await self.elastic.get('persons', id)
            return result['_source']

        except exceptions.NotFoundError:
            return None

    @backoff.on_exception(backoff.expo, Exception)
    async def get_multi(
            self, page: int, size: int, q: str = None) -> List[Optional[Dict]]:
        query = {'size': size, 'from': (page - 1) * size}

        if q:
            query['query'] = {
                "bool": {
                    "must": [
                        {
                            "match": {
                                "full_name": q
                            }
                        }
                    ]
                }
            }
        else:
            query['query'] = {"match_all": {}}

        try:
            doc = await self.elastic.search(index='persons', body=query)

        except exceptions.NotFoundError:
            logging.debug('index not found')
            return []

        if not doc:
            return []
        result = doc['hits']['hits']

        if not result:
            return []

        return [person['_source'] for person in result]
