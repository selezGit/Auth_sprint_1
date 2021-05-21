import repackage
repackage.up()

import asyncio
from elasticsearch import AsyncElasticsearch

repackage.up()
from settings import SETTINGS, logger


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
    repackage.up()
    from settings import SETTINGS, logger
    asyncio.run(wait_es())
