import logging

from pydantic import BaseSettings, Field

logger = logging.getLogger('tests')
logging.getLogger('elasticsearch').setLevel(logging.CRITICAL)
logging.getLogger('asyncio').setLevel(logging.CRITICAL)
logger.setLevel('DEBUG')


def singleton(class_):
    instances = {}

    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]
    return getinstance


@singleton
class TestSettings(BaseSettings):
    back_host: str = Field('http://back:8000', env='FASTAPI_HOST')
    es_host: str = Field('elasticsearch:9200', env='ELASTIC_HOST')
    redis_host: str = Field('redis', env='REDIS_HOST')
    redis_port: str = Field('6379', env='REDIS_PORT')


SETTINGS = TestSettings()
