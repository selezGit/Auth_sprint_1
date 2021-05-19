from functools import lru_cache
from typing import Dict, List, Optional

from aioredis import Redis
from cache.base import BaseCache
from cache.redis_cache import RedisCache
from db.elastic import get_elastic
from db.redis import get_redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from storage.genre import GenreBaseStorage, GenreElasticStorage

from services.base import BaseService


class GenreService(BaseService):
    def __init__(self, cache: BaseCache, storage: GenreBaseStorage):
        self.cache = cache
        self.storage = storage

    async def get_by_id(self, url: str, id: str) -> Optional[Dict]:
        """Получить объект по uuid"""
        data = await self.cache.check_cache(url)
        if not data:
            data = await self.storage.get(id=id)
            if data:
                await self.cache.load_cache(url, data)

        return data

    async def get_by_param(
        self, url: str, page: int, size: int
    ) -> List[Optional[Dict]]:

        data = await self.cache.check_cache(url)
        if not data:
            data = await self.storage.get_multi(page=page, size=size)
            if data:
                await self.cache.load_cache(url, data)

        return data


@lru_cache()
def get_genre_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    cache = RedisCache(redis)
    storage = GenreElasticStorage(elastic)
    return GenreService(cache, storage)
