import json
from http import HTTPStatus
from typing import Dict
from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends, HTTPException
from pydantic.tools import lru_cache
from core.config import FILM_CACHE_EXPIRE_IN_SECONDS
from db.elastic import get_elastic
from db.redis import get_redis
from models.film import Person


class PersonService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_person_by_id(self, redis_key, person_id: str):
        films = await self._person_from_cache(redis_key)
        if films is not None:
            return films
        result = {'id': person_id}
        result['full_name'] = await self._get_person_full_name_by_id(person_id)
        if result['full_name'] is None:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='person not found')
        types = [
            ('director', 'director'),
            ('actors_names', 'actor'),
            ('writers_names', 'writer'),
        ]
        result['roles'] = dict()
        for t in types:
            result['roles'][t[1]] = await self._get_films_by_person_full_name(
                type=t[0], person_name=result['full_name']
            )
        await self._put_result_to_cache(redis_key, result)
        return result

    # http://localhost:8106/api/v1/persons/search/?query=Mary&page[number]=1&page[size]=50
    async def search_person_by_query(self, redis_key, query, pagination):
        films = await self._person_from_cache(redis_key)
        if films is not None:
            return films
        persons = await self._get_persons_by_search_query_elastic(
            query, pagination.offset, pagination.limit
        )
        if persons is None:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='person not found')
        persons = [i['_source']['full_name'] for i in persons]
        with open('log.json', mode='w') as f:
            f.write(json.dumps(persons))
        results = []
        for person in persons:
            result = dict()
            result['id'] = '86f1f44b-39f5-41a6-8b3b-af5a9ed09858'
            result['full_name'] = person
            types = [
                ('director', 'director'),
                ('actors_names', 'actor'),
                ('writers_names', 'writer'),
            ]
            result['roles'] = dict()
            for t in types:
                result['roles'][t[1]] = await self._get_films_by_person_full_name(
                    type=t[0], person_name=result['full_name']
                )

            person = Person(**result)
            results.append(person)
        await self._put_result_to_cache(redis_key, results)
        return results

    async def get_films_by_person_id(
        self, redis_key, offset=0, limit=10, person_id=None, sort=None
    ):
        films = await self._person_from_cache(redis_key)
        if films is not None:
            return films
        full_name = await self._get_person_full_name_by_id(person_id)
        if full_name is None:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='person not found')
        result = list()
        for i in ['director', 'actors_names', 'writers_names']:
            response = await self._get_movies_from_elastic(offset, limit, {i: full_name}, sort)
            result.extend(response['hits']['hits'])

        roles = sorted(result, key=lambda x: x['sort'], reverse=True)
        await self._put_result_to_cache(redis_key, roles)
        return roles

    async def _get_person_full_name_by_id(self, person_id: str):
        query_body = {'query': {'match': {'id': person_id}}}
        result = await self.elastic.search(index='persons', body=query_body)
        try:
            return result['hits']['hits'][0]['_source']['full_name']
        except IndexError:
            return None

    async def _get_films_by_person_full_name(self, type, person_name: str):
        query_body = {'query': {'match_phrase': {type: person_name}}}
        try:
            result = await self.elastic.search(index='movies', body=query_body)

            if len(result['hits']['hits']) > 0:
                return [i['_id'] for i in result['hits']['hits']]
            else:
                return None
        except Exception:
            return None

    async def _get_movies_from_elastic(
        self, offset: int = 0, limit: int = 10, filter_by: Dict = None, sort: Dict = None
    ):

        if sort is None:
            sort = {'imdb_rating': 'desc'}

        if filter_by is None:
            query_body = {
                'query': {'match_all': {},},
                'sort': {**sort},
            }
            result = await self.elastic.search(
                index='movies', body=query_body, from_=offset, size=limit
            )
            return result
        else:
            query_body = {
                'query': {'bool': {'filter': {'match': {**filter_by}}}},
                'sort': {**sort},
            }
            result = await self.elastic.search(
                index='movies', body=query_body, from_=offset, size=limit
            )

            return result

    async def _get_persons_by_search_query_elastic(
        self, query: str, offset: int = 0, limit: int = 10,
    ):

        query_body = {
            'query': {'query_string': {'default_field': 'full_name', 'query': query},},
        }
        result = await self.elastic.search(
            index='persons', body=query_body, from_=offset, size=limit
        )

        if len(result['hits']['hits']) == 0:
            return None
        return result['hits']['hits']

    async def _person_from_cache(self, redis_key: str):
        data = await self.redis.get(redis_key)
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
                await self.redis.set(redis_key, value=d, expire=FILM_CACHE_EXPIRE_IN_SECONDS)
            except Exception as e:
                print('exep', e)


@lru_cache()
def get_persons_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(redis, elastic)
