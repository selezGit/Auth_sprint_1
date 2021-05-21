from typing import Any, Optional
from cache.base import BaseCache
import backoff
from aioredis import Redis
import json


class RedisCache(BaseCache):

    def __init__(self, redis: Redis, expire: int = None):
        self.redis = redis
        self.expire = expire or self.FILM_CACHE_EXPIRE_IN_SECONDS

    @backoff.on_exception(backoff.expo, Exception)
    async def check_cache(self,
                          url: str,
                          ) -> Optional[Any]:
        """Найти обьекты в кэше."""
        result = await self.redis.get(str(url), )
        if result:
            result = json.loads(result)
        return result

    @backoff.on_exception(backoff.expo, Exception)
    async def load_cache(self,
                         url: str,
                         data: Any):
        """Запись объектов в кэш."""
        data = json.dumps(data)
        await self.redis.set(key=str(url), value=data, expire=self.expire)