import abc
from typing import Any


class BaseService:
    @abc.abstractmethod
    async def get_by_id(self, *args, **kwargs) -> Any:
        """Получить объект по uuid"""
        pass

    @abc.abstractmethod
    async def get_by_param(self, *args, **kwargs) -> Any:
        """Получить объекты по параметрам"""
        pass
