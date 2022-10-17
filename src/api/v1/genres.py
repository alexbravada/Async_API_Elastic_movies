from http import HTTPStatus
from pprint import pprint

from fastapi import APIRouter, Depends, HTTPException
from pydantic import ValidationError
from models.film import AllGenres, Genre
from models.paginators import PaginateModel

from services.genres import GenreService, get_genre_service


router = APIRouter()


@router.get(path='', response_model=AllGenres, summary='Returns all Genres')
async def get_genres(
    pagination: PaginateModel = Depends(PaginateModel),
    genre_service: GenreService = Depends(get_genre_service),
):
    """returns genres with names and genre.uuid"""
    redis_key = f'api/v1/genres:pnum={pagination.page_number}:psize={pagination.page_size}'
    genres = await genre_service.get_genres(redis_key)
    if not genres:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Genres not found')

    genre_name_id = [
        {'id': genre.get('_id'), 'name': genre.get('_source').get('name')}
        for genre in genres['hits']['hits']
    ]
    output = AllGenres(results=genre_name_id)
    return output


@router.get(path='/{genre_id}', response_model=Genre, summary='Get Genre')
async def get_by_id(genre_id: str, genre_service: GenreService = Depends(get_genre_service)):
    """returns info about single genre"""
    redis_key = f'api/v1/genres/{genre_id}'
    genre = await genre_service.get_genre_by_id(redis_key=redis_key, genre_id=genre_id)
    try:
        genre_body = genre['hits']['hits'][0]
    except IndexError as ind_err:
        pprint({'error': ind_err})
        genre_body = None
    if not genre_body:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail=f'genre with id {genre_id} not found'
        )
    try:
        genre_body = {
            'id': genre_body.get('_id'),
            'name': genre_body.get('_source').get('name'),
        }
        output = Genre(**genre_body)
    except ValidationError as val_er:
        pprint({'val error': val_er})
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f'{val_er.errors}')
    return output
