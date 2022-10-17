from typing import Dict, List, Optional
import orjson
import uuid
from pydantic import BaseModel, Field


def orjson_dumps(v, *, default):
    # orjson.dumps возвращает bytes, а pydantic требует unicode, поэтому декодируем
    return orjson.dumps(v, default=default).decode()


class BaseOrjsonModel(BaseModel):
    class Config:
        # Заменяем стандартную работу с json на более быструю
        # json_encoders = {id: uuid4}
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class UUIDMixin(BaseOrjsonModel):
    id: uuid.UUID


class UUIDNameMixin(UUIDMixin):
    name: str


class Film(UUIDMixin):
    """
        подробная информация о фильме
        /api/v1/films/<uuid:UUID>/
    """

    title: str
    description: Optional[str] = ''
    imdb_rating: Optional[float] = Field(default=0.0, example=88.41)
    genre: Optional[List[str]] = Field(example=['Comedy', 'Fantasy'])
    director: List[str]
    actors_names: Optional[List[str]] = []
    writers_names: Optional[List[str]] = []
    actors: Optional[List[UUIDNameMixin]] = []
    writers: Optional[List[UUIDNameMixin]] = []


class FilmShort(UUIDMixin):
    """
       Поиск, фильтр и отображение фильмов на главной странице.
       GET /api/v1/films?sort=-imdb_rating&page[size]=50&page[number]=1
       GET /api/v1/films/search/
       GET /api/v1/persons/<uuid:UUID>/film/ фильмы в которых учавствовал person.
       Жанр и популярные фильмы в нём. Это просто фильтрация.
       /api/v1/films?sort=-imdb_rating&filter[genre]=<comedy-uuid>
    """

    title: str
    imdb_rating: Optional[float] = Field(default=0.0, example=88.41)


class AllFilms(BaseOrjsonModel):
    results: List[FilmShort]


class AllShortFilms(BaseOrjsonModel):
    page_size: int
    page_number: int
    filter: Optional[dict] = {}
    sort: Optional[dict] = {}
    results: List[FilmShort]
    amount_results: Optional[int] = 0


class ByRoles(BaseOrjsonModel):
    roles: Dict


class Person(UUIDMixin, ByRoles):
    full_name: str


class Persons(BaseOrjsonModel):
    results: List[Person] = []


class Genre(UUIDNameMixin):
    """Данные по конкретному жанру.
       /api/v1/genres/<uuid:UUID>/ 
    """


class AllGenres(BaseOrjsonModel):
    results: List[Genre] = []


class GenrePopularFilms(Genre):
    """
        Популярные фильмы в жанре.
        /api/v1/films...
    """

    top_films: List[FilmShort]
