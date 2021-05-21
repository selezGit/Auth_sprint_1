from enum import Enum
from http import HTTPStatus
from typing import List, Optional

from api.v1.base_view import BaseView
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from models.film import Film, FilmShort
from pydantic import UUID4
from services.film import FilmService, get_film_service

router = APIRouter()


class Order(str, Enum):
    desc = "DESC"
    asc = "ASC"


class FilmView(BaseView):
    @router.get(
        "/", response_model=List[Film], summary="Получение списка фильмов с параметрами"
    )
    async def get_all(
        order: Optional[Order] = Order.desc,
        genre: Optional[UUID4] = None,
        size: Optional[int] = Query(50, gt=0, le=10000),
        page: Optional[int] = Query(1, gt=0, le=100),
        query: Optional[str] = None,
        request: Request = None,
        film_service: FilmService = Depends(get_film_service),
    ) -> Optional[List[FilmShort]]:
        """Возвращает короткую информацию по всем фильмам, отсортированным по рейтингу,
        есть возможность фильтровать фильмы по id жанров"""
        films = await film_service.get_by_param(
            url=str(request.url), order=order, genre=genre, page=page, size=size, query=query
        )

        if not films:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND, detail="film not found"
            )

        return films

    @router.get("/{film_id}", response_model=Film, summary="Фильм")
    async def get_details(
        film_id: UUID4,
        request: Request = None,
        film_service: FilmService = Depends(get_film_service),
    ) -> Film:
        """Возвращает информацию по одному фильму"""
        film = await film_service.get_by_id(url=str(request.url), id=film_id)
        if not film:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND, detail="film not found"
            )
        return film
