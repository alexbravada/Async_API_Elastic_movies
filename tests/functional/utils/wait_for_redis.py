import time

import aioredis
from tests.functional.settings import test_settings

if __name__ == '__main__':
    redis = await aioredis.create_redis_pool(
        (test_settings.redis_host, int(test_settings.redis_port)), minsize=10, maxsize=20
    )

    time.sleep(1)

    while True:
        if redis.ping():
            break
        time.sleep(1)
