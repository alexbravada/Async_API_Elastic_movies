import logging
import aioredis

from tests.functional.settings import test_settings
from tests.functional.utils.backoff import backoff

logging.basicConfig(
    filename='es_ping.log',
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
    level=logging.INFO
)


@backoff(log=logging, exception=Exception)
def wait_for_redis(redis):
    while True:
        if redis.ping():
            break


if __name__ == '__main__':
    redis = await aioredis.create_redis_pool(
        (test_settings.redis_host, int(test_settings.redis_port)), minsize=10, maxsize=20
    )

    wait_for_redis(redis)

    redis.close()
