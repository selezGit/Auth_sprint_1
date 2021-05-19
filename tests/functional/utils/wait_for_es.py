from settings import SETTINGS, logger
import asyncio

import repackage
from elasticsearch import AsyncElasticsearch

repackage.up()


async def wait_es():
    client = AsyncElasticsearch(hosts=[SETTINGS.es_host, ])
    response = await client.ping()
    while not response:
        await asyncio.sleep(2)
        logger.info('Elastic is unavailable - sleeping')
        response = await client.ping()
    await client.close()
    logger.info("Elastic is run!")


if __name__ == '__main__':
    asyncio.run(wait_es())
