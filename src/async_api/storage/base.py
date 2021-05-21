import abc


class BaseStorage:
    @abc.abstractmethod
    async def get_multi(self, page: int = None, size: int = None, q: str = None):
        pass

    @abc.abstractmethod
    async def get(self, id: str):
        pass
