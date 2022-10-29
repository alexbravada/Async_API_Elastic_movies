import json
import pytest

from tests.functional.settings import test_settings_genres, test_settings_films
from ..utils.helpers import _get_from_redis_cache, _put_result_to_redis_cache


@pytest.mark.asyncio
async def test_genre_id(elasticsearch_client, session_client, redis_client):
    # 1. Генерируем данные для ES
    settings = test_settings_genres
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

    redis_key = f'api/v1/genres/{str(es_data[settings.es_id_field])}'

    redis_response = await _get_from_redis_cache(redis_client, redis_key)

    # 5. Проверяем ответ
    assert status == 200
    assert body['id'] == es_data[settings.es_id_field]
    assert redis_response['hits']['hits'][0]['_id'] == es_data[settings.es_id_field]


@pytest.mark.asyncio
async def test_genres(session_client):
    settings = test_settings_genres
    # 1. Запрашиваем данные из ES по API
    url = settings.service_url + settings.api_uri

    async with session_client.get(url) as response:
        body = await response.json()
        status = response.status

    # 5. Проверяем ответ
    assert status == 200
    assert len(body['results']) > 0


@pytest.mark.asyncio
async def test_popular_films_in_genre(elasticsearch_client, session_client, redis_client):
    # 1. Генерируем данные для ES
    g_settings = test_settings_genres
    g_es_data = g_settings.es_data[-3]
    f_settings = test_settings_films
    f_es_data = f_settings.es_data[-3]

    # добавим данные о сгенерированном жанре к сгенерированному фильму
    f_es_data['genre'].append(g_es_data['id'])
    bulk_query = [
        json.dumps({'index': {'_index': g_settings.es_index,
                              '_id': g_es_data[g_settings.es_id_field]}}),
        json.dumps(g_es_data),
        json.dumps({'index': {'_index': f_settings.es_index,
                              '_id': f_es_data[f_settings.es_id_field]}}),
        json.dumps(f_es_data)
    ]

    str_query = '\n'.join(bulk_query) + '\n'

    # 2. Загружаем данные в ES

    response = await elasticsearch_client.bulk(str_query, refresh=True)
    if response['errors']:
        raise Exception('Ошибка записи данных в Elasticsearch', response)

    # 3. Запрашиваем данные из ES по API

    url = f_settings.service_url + f_settings.api_uri + '/genre_top_films/' + \
          str(g_es_data[g_settings.es_id_field])

    async with session_client.get(url) as response:
        body = await response.json()
        status = response.status

    # 4. Загружаем кэш из Redis

    redis_key = f'api/v1/films/genre_top_films/{str(g_es_data["id"])}'

    redis_response = await _get_from_redis_cache(redis_client, redis_key)

    # 5. Проверяем ответ
    assert status == 200
    assert f_es_data['title'] == body['results'][0]['title']
