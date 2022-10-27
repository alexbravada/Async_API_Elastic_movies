import json
import os

FILM_CACHE_EXPIRE_IN_SECONDS = int(os.getenv('FILM_CACHE_EXPIRE_IN_SECONDS', 60 * 5))

async def _get_from_redis_cache(redis, redis_key: str):
    data = await redis.get(redis_key)
    out = None
    try:
        out = json.loads(data)
    except Exception as out_e:
        print('out_e', out_e)
    if not out:
        return None
    return out


async def _put_result_to_redis_cache(redis, redis_key: str, data):
    if data:
        try:
            d = json.dumps(data)
            await redis.set(redis_key, value=d, expire=FILM_CACHE_EXPIRE_IN_SECONDS)
        except Exception as e:
            print('exep', e)
