import uuid

from pydantic import BaseSettings, Field


class TestSettings(BaseSettings):
    es_host_url: str = Field('http://127.0.0.1:9200', env='ELASTIC_HOST')
    redis_host: str = Field('127.0.0.1', env='REDIS_HOST')
    redis_port: str = Field('6379', env='REDIS_PORT')
    service_url: str = Field('http://127.0.0.1:8106', env='SERVICE_HOST')


class TestSettingsFilms(TestSettings):
    es_index: str = 'movies'
    es_id_field: str = 'id'
    es_data = [{
        'id': str(uuid.uuid4()),
        'imdb_rating': 8.5,
        'genre': ['Action', 'Sci-Fi'],
        'title': 'Baaaazzzzziiiinga',
        'description': 'New World',
        'director': ['Stan'],
        'actors_names': ['Ann', 'Bob'],
        'writers_names': ['Ben', 'Howard'],
        'actors': [
            {'id': str(uuid.uuid4()), 'name': 'Ann'},
            {'id': str(uuid.uuid4()), 'name': 'Bob'}
        ],
        'writers': [
            {'id': str(uuid.uuid4()), 'name': 'Ben'},
            {'id': str(uuid.uuid4()), 'name': 'Howard'}
        ],
    } for _ in range(60)]
    api_uri = '/api/v1/films'
    query_data = {'query': 'Baaaazzzzziiiinga'}


class TestSettingsPersons(TestSettings):
    es_index: str = 'persons'
    es_id_field: str = 'id'
    es_data = [{
        'id': str(uuid.uuid4()),
        'full_name': 'Lysiy iz brazzers',
    } for _ in range(60)]
    api_uri = '/api/v1/persons'
    query_data = {'query': 'Lysiy iz brazzers'}


class TestSettingsGenres(TestSettings):
    es_index: str = 'genres'
    es_id_field: str = 'id'
    es_data = [{
        'id': str(uuid.uuid4()),
        'name': 'skazka',
    } for _ in range(5)]
    api_uri = '/api/v1/genres'


test_settings = TestSettings()
test_settings_films = TestSettingsFilms()
test_settings_persons = TestSettingsPersons()
test_settings_genres = TestSettingsGenres()
