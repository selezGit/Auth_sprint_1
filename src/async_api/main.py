import logging

import aioredis
import uvicorn as uvicorn
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI, Depends
from fastapi.responses import ORJSONResponse
from fastapi_pagination import add_pagination

from api.v1 import film, genre, person
from core import config
from core.logger import LOGGING
from db import elastic, redis

from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter


app = FastAPI(
    title=config.PROJECT_NAME,
    docs_url='/docs',
    openapi_url='/api/v1/openapi.json',
    description='Информация о фильмах, жанрах и людях участвоваших в создании произведения',
    default_response_class=ORJSONResponse,
    version='1.0.0'
)
# добавляем пагинацию нашему api
add_pagination(app)


@app.on_event('startup')
async def startup():
    # Подключаемся к базам при старте сервера
    # Подключиться можем при работающем event-loop
    # Поэтому логика подключения происходит в асинхронной функции
    # redis.redis = await aioredis_cluster.create_redis_cluster(config.REDIS_HOST)

    redis.redis = await aioredis.create_redis_pool((config.REDIS_HOST, config.REDIS_PORT), minsize=10, maxsize=20)
    await FastAPILimiter.init(redis.redis)
    elastic.es = AsyncElasticsearch(
        hosts=[f'{config.ELASTIC_HOST}:{config.ELASTIC_PORT}'])




@app.on_event('shutdown')
async def shutdown():
    # Отключаемся от баз при выключении сервера
    await redis.redis.close()
    await elastic.es.close()


# Подключаем роутер к серверу, указав префикс /v1/film
# Теги указываем для удобства навигации по документации
app.include_router(film.router, prefix='/api/v1/film', tags=['Фильмы'], dependencies=[Depends(RateLimiter(times=20, seconds=60))])
app.include_router(genre.router, prefix='/api/v1/genre', tags=['Жанры'], dependencies=[Depends(RateLimiter(times=20, seconds=60))])
app.include_router(person.router, prefix='/api/v1/person', tags=['Люди'], dependencies=[Depends(RateLimiter(times=20, seconds=60))])

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=8000,
        log_config=LOGGING,
        log_level=logging.DEBUG,
    )
