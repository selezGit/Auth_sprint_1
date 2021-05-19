import abc
from typing import Any


class BaseCache:
    FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5

    @abc.abstractmethod
    async def check_cache(self,
                          url: str):
        """Найти обьекты в кэше."""
        pass

    @abc.abstractmethod
    async def load_cache(self, url: str, data: Any):
        """Запись объектов в кэш."""
        pass
