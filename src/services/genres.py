import json
import functools

from fastapi import Depends

from db.abstract import AsyncCacheStorage
from db.abstract import AsyncSearchEngine
from db.elastic import get_elastic
from db.redis import get_redis
from core.config import FILM_CACHE_EXPIRE_IN_SECONDS


class GenreService:
    def __init__(self, cache: AsyncCacheStorage, text_search: AsyncSearchEngine):
        self.cache = cache
        self.text_search = text_search

    async def get_genres(self, redis_key):
        genres = await self._film_from_cache(redis_key)
        if genres is None:
            genres = await self._get_genres_from_elastic(
                offset=0, limit=30, filter_by=None, sort=None
            )
            if genres is None:
                return None
            await self._put_result_to_cache(redis_key, genres)
        return genres

    async def get_genre_by_id(self, redis_key, genre_id):
        genre = await self._film_from_cache(redis_key)
        if genre is None:
            genre = await self._get_genre_by_id_from_elastic(genre_id)
            if genre is None:
                return None
            await self._put_result_to_cache(redis_key, genre)
        return genre

    async def _get_genres_from_elastic(self, offset=0, limit=30, filter_by=None, sort=None):
        if filter_by is None:
            query_body = {
                'query': {'match_all': {},},
            }
            result = await self.text_search.search(
                index='genres', body=query_body, from_=offset, size=limit
            )
            return result

    async def _get_genre_by_id_from_elastic(self, genre_id: str):
        query_body = {'query': {'match': {'_id': genre_id}}}
        genre = await self.text_search.search(index='genres', body=query_body)
        return genre

    async def _put_result_to_cache(self, redis_key, data):  # TODO Проверить модель Film
        # Сохраняем данные о фильме, используя команду set
        # https://redis.io/commands/set
        # pydantic позволяет сериализовать модель в json
        if data:
            try:
                d = json.dumps(data)
                await self.cache.set(redis_key, value=d, expire=FILM_CACHE_EXPIRE_IN_SECONDS)
            except Exception as e:
                print('exep', e)

    async def _film_from_cache(self, redis_key: str):
        data = await self.cache.get(redis_key)
        out = None
        try:
            out = json.loads(data)
        except Exception as out_e:
            print('out_e', out_e)
        if not out:
            return None
        return out


# Используем lru_cache-декоратор, чтобы создать объект сервиса в едином экземпляре (синглтона)
@lru_cache()
def get_genre_service(
    cache: AsyncCacheStorage = Depends(get_redis),
    text_search: AsyncSearchEngine = Depends(get_elastic),
) -> GenreService:
    return GenreService(cache, text_search)
