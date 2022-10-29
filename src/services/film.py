from functools import cache, lru_cache
from typing import Dict, Optional
import json
from fastapi import Depends

from db.abstract import AsyncCacheStorage
from db.abstract import AsyncSearchEngine
from db.elastic import get_elastic
from db.redis import get_redis

from models.film import Film
from core.config import FILM_CACHE_EXPIRE_IN_SECONDS


class FilmService:
    def __init__(self, cache: AsyncCacheStorage, text_search: AsyncSearchEngine):
        self.cache = cache
        self.text_search = text_search

    # get_by_id возвращает объект фильма. Он опционален, так как фильм может отсутствовать в базе
    async def get_by_id(self, redis_key: str, film_id: str) -> Optional[Film]:
        film = await self._film_from_cache(redis_key)
        if not film:
            # Если фильма нет в кеше, то ищем его в Elasticsearch
            # film = await self._get_film_from_elastic(film_id)
            film = await self._get_movie_by_id(film_id)
            if not film:
                # Если он отсутствует в Elasticsearch, значит, фильма вообще нет в базе
                return None
            # Сохраняем фильм  в кеш
            await self._put_result_to_cache(redis_key, film)
        return film

    async def get_paginated_movies(
        self, redis_key, offset=0, limit=10, filter_by=None, sort=None
    ):
        film = await self._film_from_cache(redis_key)
        if film is None:
            film = await self._get_movies_from_elastic(offset, limit, filter_by, sort)
            if film is None:
                return None
            await self._put_result_to_cache(redis_key, film)
        return film

    async def get_top_films_by_genre_id(self, redis_key, genre_id, pagination):
        films = await self._film_from_cache(redis_key)
        if films is None:
            films = await self._get_films_by_genre_id_from_elastic(
                genre_id, pagination.offset, pagination.limit
            )
            if films is None:
                return None
            await self._put_result_to_cache(redis_key, films)
        return films

    async def get_items_by_query(self, redis_key, query, pagination):
        films = await self._film_from_cache(redis_key)
        if films is None:
            films = await self._get_films_by_search_query_elastic(
                query, pagination.offset, pagination.limit
            )
            if films is None:
                return None
            await self._put_result_to_cache(redis_key, films)
        return films

    async def _get_films_by_search_query_elastic(
        self,
        query: str,
        offset: int = 0,
        limit: int = 10,
        filter_by: Dict = None,
        sort: Dict = None,
    ):
        if filter_by is None:
            default_fields_list = [
                'title',
                'description',
                'writers_names',
                'actors_names',
                'director',
            ]
            query_body = {
                'query': {'query_string': {'fields': default_fields_list, 'query': query},},
            }
            result = await self.text_search.search(
                index='movies', body=query_body, from_=offset, size=limit
            )
            if len(result['hits']['hits']) == 0:
                return None
        return result

    async def _get_movie_by_id(self, film_id: str):
        query_body = {'query': {'match': {'id': film_id}}}
        result = await self.text_search.search(index='movies', body=query_body)
        try:
            film = result['hits']['hits'][0]
        except IndexError:
            return None
        return result

    async def _get_films_by_genre_id_from_elastic(
        self, genre_id, offset=0, limit=15, filter_by=None, sort=None
    ):
        sort = {'imdb_rating': 'desc'}
        query_body = {'query': {'match': {'genre': genre_id}}, 'sort': [sort]}
        result = await self.text_search.search(
            index='movies', body=query_body, from_=offset, size=limit
        )
        if len(result['hits']['hits']) == 0:
            return None
        return result

    async def _get_movies_from_elastic(
        self, offset: int = 0, limit: int = 10, filter_by: Dict = None, sort: Dict = None
    ):

        if sort is None:
            sort = {'imdb_rating': 'desc'}

        if filter_by is None:
            query_body = {
                'query': {'match_all': {},},
                'sort': [sort],
            }
            result = await self.elastic.search(
                index='movies', body=query_body, from_=offset, size=limit
            )
            return result
        else:
            query_body = {
                'query': {'bool': {'filter': {'match': {**filter_by}}}},
                'sort': [sort],
            }
            result = await self.elastic.search(
                index='movies', body=query_body, from_=offset, size=limit
            )

            return result

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

    async def _put_result_to_cache(self, redis_key, data):
        # Сохраняем данные о фильме, используя команду set
        # https://redis.io/commands/set
        # pydantic позволяет сериализовать модель в json
        if data:
            try:
                d = json.dumps(data)
                await self.cache.set(redis_key, value=d, expire=FILM_CACHE_EXPIRE_IN_SECONDS)
            except Exception as e:
                print('exep', e)


# get_film_service — это провайдер FilmService.
# С помощью Depends он сообщает, что ему необходимы Redis и Elasticsearch
# Для их получения вы ранее создали функции-провайдеры в модуле db
# Используем lru_cache-декоратор, чтобы создать объект сервиса в едином экземпляре (синглтона)
@lru_cache()
def get_film_service(
    cache: AsyncCacheStorage = Depends(get_redis),
    text_search: AsyncSearchEngine = Depends(get_elastic),
) -> FilmService:
    return FilmService(cache, text_search)
