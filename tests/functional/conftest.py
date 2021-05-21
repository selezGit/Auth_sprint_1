import asyncio
import time
from typing import Any

import aiohttp
import aioredis
import pytest
from elasticsearch import AsyncElasticsearch, exceptions, helpers

from settings import SETTINGS, logger
from testdata.models import HTTPResponse
from utils.bulk_helper import delete_doc, generate_doc
from utils.wait_for_es import wait_es
from utils.wait_for_redis import wait_redis

SERVICE_URL = 'http://127.0.0.1:8000'


@pytest.fixture(scope='function')
async def es_client():
    await wait_es()
    client = AsyncElasticsearch(hosts=[SETTINGS.es_host, ])
    yield client
    await client.close()


@pytest.fixture(scope='function')
async def session():
    async with aiohttp.ClientSession() as session:
        yield session
    await session.close()


@pytest.fixture(scope='function')
async def redis_client():
    await wait_redis()
    client = await aioredis.create_redis_pool((SETTINGS.redis_host, SETTINGS.redis_port), minsize=10, maxsize=20)
    yield client
    client.close()


@pytest.fixture
async def make_get_request(session, redis_client):
    async def inner(method: str, params: dict = None, cleaning_redis: bool = True) -> HTTPResponse:
        params = params or {}
        # в боевых системах старайтесь так не делать!
        url = SETTINGS.back_host + '/api/v1' + method
        start = time.time()
        async with session.get(url, params=params) as response:
            #  очищаем кэш redis
            if cleaning_redis:
                await redis_client.delete(str(response.url))

            return HTTPResponse(
                body=await response.json(),
                headers=response.headers,
                status=response.status,
                url=response.url,
                resp_speed=(time.time()-start))

    return inner


@pytest.fixture(scope='function')
async def prepare_es_film(es_client):
    index = 'movies'
    data = [{'id': '3a5f9a83-4b74-48be-a44e-a6c8beee9460',
             'title': 'abracadabra',
             'description': '',
             'imdb_rating': 0,
             'creation_date': '1970-01-01T00:00:00',
             'restriction': 0,
             'directors': [],
             'actors': [{
                 'id': '7f489c61-1a21-43d2-a3ad-3d900f8a9b5e',
                 'name': 'Test Testovich'
             }],
             'writers': [],
             'genres': [],
             'file_path': ''}]

    await helpers.async_bulk(es_client, generate_doc(data, index))
    logger.info('movie is uploaded')
    # ждём секунду, что бы данные успели загрузиться в elastic
    await asyncio.sleep(1)

    yield data

    # удаляем загруженные в elastic данные
    await helpers.async_bulk(es_client, delete_doc(data, index))
    logger.info('movie is deleted')


@pytest.fixture(scope='function')
async def prepare_es_genre(es_client):
    index = 'genre'
    data = [{'id': 'e91db2b1-d967-4785-bec9-1eade1d56243',
             'name': 'Test genre'}]

    await helpers.async_bulk(es_client, generate_doc(data, index))
    logger.info('genre is uploaded')
    # ждём секунду, что бы данные успели загрузиться в elastic
    await asyncio.sleep(1)

    yield data

    await helpers.async_bulk(es_client, delete_doc(data, index))
    logger.info('genre is deleted')


@pytest.fixture(scope='function')
async def prepare_es_person(es_client):
    index = 'persons'
    data = [{'id': '7f489c61-1a21-43d2-a3ad-3d900f8a9b5e',
            'full_name': 'Test Testovich',
             'role': ['actor'],
             'film_ids': ['3a5f9a83-4b74-48be-a44e-a6c8beee9460']}]

    await helpers.async_bulk(es_client, generate_doc(data, index))
    logger.info('person is uploaded')
    # ждём секунду, что бы данные успели загрузиться в elastic
    await asyncio.sleep(1)

    yield data

    await helpers.async_bulk(es_client, delete_doc(data, index))
    logger.info('person is deleted')


@pytest.fixture
async def get_all_data_elastic(es_client):
    async def inner(index: str) -> Any:
        query = {
            "query": {
                "match_all": {}
            }
        }

        try:
            doc = await es_client.search(index=index, body=query, size=10000)
        except exceptions.NotFoundError:
            return []

        if not doc:
            return []
        result = doc["hits"]["hits"]

        if not result:
            return []

        return [data["_source"] for data in result]
    return inner
