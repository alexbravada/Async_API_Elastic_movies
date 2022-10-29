import json
from http import HTTPStatus

import pytest

from tests.functional.settings import test_settings_films, test_settings_persons
from ..utils.helpers import _get_from_redis_cache, _put_result_to_redis_cache


#  Название теста должно начинаться со слова `test_`
#  Любой тест с асинхронными вызовами нужно оборачивать декоратором `pytest.mark.asyncio`, который следит за запуском и работой цикла событий.

@pytest.mark.asyncio
async def test_search_films(elasticsearch_client, session_client, redis_client):
    # 1. Генерируем данные для ES
    settings = test_settings_films
    es_data = settings.es_data
    bulk_query = []
    for row in es_data[:50]:
        bulk_query.extend([
            json.dumps({'index': {'_index': settings.es_index,
                                  '_id': row[settings.es_id_field]}}),
            json.dumps(row)
        ])
    str_query = '\n'.join(bulk_query) + '\n'

    # 2. Загружаем данные в ES
    response = await elasticsearch_client.bulk(str_query, refresh=True)
    if response['errors']:
        raise Exception('Ошибка записи данных в Elasticsearch', response)

    # 3. Запрашиваем данные из ES по API
    url = settings.service_url + settings.api_uri + '/search/'
    async with session_client.get(url, params=settings.query_data) as response:
        body = await response.json()
        status = response.status

    # 4. Загружаем кэш из Redis
    redis_key = f'api/v1/films/search:query={settings.query_data["query"]}:pnum=1:psize=50'
    redis_response = await _get_from_redis_cache(redis_client, redis_key)

    # 5. Проверяем ответ
    assert status == HTTPStatus.OK
    assert len(body['results']) == 50
    assert len(redis_response['hits']['hits']) == 50


@pytest.mark.asyncio
async def test_search_persons(elasticsearch_client, session_client, redis_client):
    # 1. Генерируем данные для ES
    settings = test_settings_persons
    es_data = settings.es_data
    bulk_query = []
    for row in es_data[:50]:
        bulk_query.extend([
            json.dumps({'index': {'_index': settings.es_index,
                                  '_id': row[settings.es_id_field]}}),
            json.dumps(row)
        ])
    str_query = '\n'.join(bulk_query) + '\n'

    # 2. Загружаем данные в ES
    response = await elasticsearch_client.bulk(str_query, refresh=True)
    if response['errors']:
        raise Exception('Ошибка записи данных в Elasticsearch', response)

    # 3. Запрашиваем данные из ES по API
    url = settings.service_url + settings.api_uri + '/search/'
    async with session_client.get(url, params=settings.query_data) as response:
        body = await response.json()
        status = response.status

    # 4. Загружаем кэш из Redis
    redis_key = f'api/v1/persons/search:query={settings.query_data["query"]}:pnum=1:psize=50'
    redis_response = await _get_from_redis_cache(redis_client, redis_key)

    # 5. Проверяем ответ
    assert status == HTTPStatus.OK
    assert len(body['results']) == 50
    assert len(redis_response) == 50
