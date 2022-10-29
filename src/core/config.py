import os

from logging import config as logging_config
from typing import List, Dict, Any
from fastapi.responses import ORJSONResponse
from core.logger import LOGGING
from pydantic import BaseSettings, RedisDsn, Field

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)

# Название проекта. Используется в Swagger-документации
PROJECT_NAME = os.getenv('PROJECT_NAME', 'movies')

# Настройки Redis
REDIS_HOST = os.getenv('REDIS_HOST', '127.0.0.1')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))

# Настройки Elasticsearch
ELASTIC_HOST = os.getenv('ELASTIC_HOST', '127.0.0.1')
ELASTIC_PORT = int(os.getenv('ELASTIC_PORT', 9200))

# Время жизни кэшированного запроса
FILM_CACHE_EXPIRE_IN_SECONDS = int(os.getenv('FILM_CACHE_EXPIRE_IN_SECONDS', 60 * 5))  # 5 минут

# Корень проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Settings(BaseSettings):
    debug: bool = False
    docs_url: str = '/doc'
    openapi_prefix: str = ''
    openapi_url: str = '/openapi.json'
    redoc_url: str = '/redoc'
    title: str = 'FastAPI Sprint 1 module 2'
    version: str = "1.0"
    default_response_class = ORJSONResponse

    redis_uri: RedisDsn = 'redis://127.0.0.1:6379'
    REDIS_HOST: str = Field('127.0.0.1', env='REDIS_HOST')
    REDIS_PORT: str = Field('6379', env='REDIS_PORT')
    elastic_uri: str = ''
    ELASTIC_HOST: str = Field('127.0.0.1', env='ELASTIC_HOST')
    ELADTIC_PORT: int = Field(9200, env='ELASTIC_PORT')

    allowed_hosts: List[str] = ["*"]

    class Config:
         env_file = '.env'

    @property
    def fastapi_kwargs(self) -> Dict[str, Any]:
        return {
            "debug": self.debug,
            "docs_url": self.docs_url,
            "openapi_prefix": self.openapi_prefix,
            "openapi_url": self.openapi_url,
            "redoc_url": self.redoc_url,
            "title": self.title,
            "version": self.version,
            "default_response_class": self.default_response_class,
        }
