import json
from http import HTTPStatus

import pytest

from tests.functional.settings import test_settings_films
from ..utils.helpers import _get_from_redis_cache, _put_result_to_redis_cache


@pytest.mark.asyncio
async def test_film_id(elasticsearch_client, session_client, redis_client):
    # 1. Генерируем данные для ES
    settings = test_settings_films
    es_data = settings.es_data[-1]
    bulk_query = [
        json.dumps({'index': {'_index': settings.es_index,
                              '_id': es_data[settings.es_id_field]}}),
        json.dumps(es_data)
    ]
    str_query = '\n'.join(bulk_query) + '\n'

    # 2. Загружаем данные в ES
    response = await elasticsearch_client.bulk(str_query, refresh=True)
    if response['errors']:
        raise Exception('Ошибка записи данных в Elasticsearch', response)

    # 3. Запрашиваем данные из ES по API
    url = settings.service_url + settings.api_uri + '/' + str(es_data[settings.es_id_field])
    async with session_client.get(url) as response:
        body = await response.json()
        status = response.status

    # 4. Загружаем кэш из Redis
    redis_key = f'api/v1/films/{str(es_data[settings.es_id_field])}'
    redis_response = await _get_from_redis_cache(redis_client, redis_key)

    # 5. Проверяем ответ
    assert status == HTTPStatus.OK
    assert body['id'] == es_data[settings.es_id_field]
    assert redis_response['hits']['hits'][0]['_id'] == es_data[settings.es_id_field]


@pytest.mark.asyncio
async def test_films(session_client):
    settings = test_settings_films
    # 1. Запрашиваем данные из ES по API
    url = settings.service_url + settings.api_uri
    async with session_client.get(url) as response:
        body = await response.json()
        status = response.status

    # 2. Проверяем ответ
    assert status == HTTPStatus.OK
    assert len(body['results']) == 50
    # правильность сортировки
    assert body['results'] == sorted(body['results'], key=lambda x: x['imdb_rating'], reverse=True)
