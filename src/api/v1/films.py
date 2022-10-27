from http import HTTPStatus

from fastapi import APIRouter, Depends, Request, HTTPException
from models.film import AllShortFilms, Film, FilmShort
from models.paginators import PaginateModel
from models.query_filters import QueryFilterModel

from services.film import FilmService, get_film_service


router = APIRouter()


@router.get(
    path='/{film_id}',
    response_model=Film,
    description='Film detail informations',
    summary='Get full film info by id(uuid)',
)
async def film_details(
    film_id: str, film_service: FilmService = Depends(get_film_service)
) -> Film:
    redis_key = f'api/v1/films/{film_id}'
    film = await film_service.get_by_id(redis_key, film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='film not found')
    film = Film(**film['hits']['hits'][0].get('_source'))
    return film


# http://127.0.0.1:8104/api/v1/films?filter[genre]=Comedy&page[size]=3&page[number]=6&sort=-imdb_rating&sort=created
@router.get(path='', response_model=AllShortFilms, summary='All films with main info')
async def get_film_list(
    filter_by: QueryFilterModel = Depends(QueryFilterModel),
    pagination: PaginateModel = Depends(PaginateModel),
    film_service: FilmService = Depends(get_film_service),
) -> AllShortFilms:
    """Returns list of films with id, title, imdb_rating """
    redis_key = f'api/v1/films/pnum:{pagination.page_number}-psize:{pagination.page_size}-filter:{filter_by.filter_by_genre}:{filter_by.filter_by_director}'
    film = await film_service.get_paginated_movies(
        redis_key,
        offset=pagination.offset,
        limit=pagination.page_size,
        filter_by=filter_by.get_filter_for_elastic(),
    )

    to_res = [FilmShort(**source['_source']) for source in film['hits']['hits']]
    amount = film['hits']['total']['value']
    responce = AllShortFilms(
        page_size=pagination.page_size,
        page_number=pagination.page_number,
        results=to_res,
        amount_results=amount,
    )
    return responce


@router.get(
    path='/search/',
    response_model=AllShortFilms,
    summary='Search match films from words in query',
)
async def search_film_by_query(
    query: str,
    pagination: PaginateModel = Depends(PaginateModel),
    film_service: FilmService = Depends(get_film_service),
) -> AllShortFilms:
    """Use /?query=Matrix Revolution"""
    redis_key = f'api/v1/films/search:query={query}:pnum={pagination.page_number}:psize={pagination.page_size}'
    film = await film_service.get_items_by_query(
        redis_key=redis_key, query=query, pagination=pagination
    )
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='film by query not found')
    search_res = [FilmShort(**source['_source']) for source in film['hits']['hits']]
    amount = film['hits']['total']['value']
    responce = AllShortFilms(
        results=search_res,
        amount_results=amount,
        page_size=pagination.page_size,
        page_number=pagination.page_number,
    )
    return responce


# Популярные фильмы в жанре.
# /api/v1/films/genre_top_films/{genre_id}
@router.get(
    path='/genre_top_films/{genre_id}',
    response_model=AllShortFilms,
    summary='Returns top films from genre (uuid)',
)
async def get_top_films_by_genre(
    genre_id: str,
    pagination: PaginateModel = Depends(PaginateModel),
    film_service: FilmService = Depends(get_film_service),
):
    """Returns list of top films of genre, sorted by imdb_rating from top to bottom rating"""
    redis_key = f'api/v1/films/genre_top_films/{genre_id}:pnum:{pagination.page_number}-psize:{pagination.page_size}'
    films = await film_service.get_top_films_by_genre_id(
        redis_key=redis_key, genre_id=genre_id, pagination=pagination
    )
    if not films:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='top-films by genre not found'
        )
    to_res = [FilmShort(**source['_source']) for source in films['hits']['hits']]
    amount_match = films['hits']['total']['value']
    result = AllShortFilms(
        results=to_res,
        page_number=pagination.page_number,
        page_size=pagination.page_size,
        amount_results=amount_match,
    )
    return result
