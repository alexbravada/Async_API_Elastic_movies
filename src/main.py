import logging

import aioredis
import uvicorn
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from api import router as api_router
from core import config
from core.logger import LOGGING
from db import elastic, redis

settings = config.Settings()

app = FastAPI(**settings.fastapi_kwargs)

@app.on_event('startup')
async def startup():
    redis.redis = await aioredis.create_redis_pool(
        (settings.REDIS_HOST, settings.REDIS_PORT), minsize=10, maxsize=20
    )
    elastic.es = AsyncElasticsearch(hosts=[f'{settings.ELASTIC_HOST}:{settings.ELADTIC_PORT}'])


@app.on_event('shutdown')
async def shutdown():
    redis.redis.close()
    await redis.redis.wait_closed()
    await elastic.es.close()


app.include_router(api_router, prefix='/api', tags=['v1'])

if __name__ == '__main__':
    # Приложение может запускаться командой
    # `uvicorn main:app --host 0.0.0.0 --port 8000`
    # но чтобы не терять возможность использовать дебагер,
    # запустим uvicorn сервер через python
    uvicorn.run(
        'main:app', host='0.0.0.0', port=8000, log_config=LOGGING, log_level=logging.DEBUG,
    )
