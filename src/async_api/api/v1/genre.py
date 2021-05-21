import uuid
from http import HTTPStatus
from typing import List, Optional

from api.v1.base_view import BaseView
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import UUID4, BaseModel
from services.genre import GenreService, get_genre_service

router = APIRouter()


class Genre(BaseModel):
    id: uuid.UUID
    name: str


class GenreView(BaseView):
    @router.get("/", response_model=List[Genre], summary="Список жанров")
    async def get_all(
            size: Optional[int] = Query(default=50, ge=1, le=500),
            page: Optional[int] = Query(default=1, ge=1),
            request: Request = None,
            genre_service: GenreService = Depends(get_genre_service),
    ) -> Optional[List[Genre]]:
        """Возвращает инф-ию по всем жанрам с возможностью пагинации"""

        genres = await genre_service.get_by_param(
            url=str(request.url), page=page, size=size
        )
        if not genres:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND, detail="genre not found"
            )

        return genres

    @router.get("/{genre_id}", response_model=Genre, summary="Жанр")
    async def get_details(
            genre_id: UUID4,
            request: Request = None,
            genre_service: GenreService = Depends(get_genre_service),
    ) -> Genre:
        """Возвращает информацию по одному жанру"""
        genre = await genre_service.get_by_id(url=str(request.url), id=str(genre_id))
        if not genre:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND, detail="genre not found"
            )
        return genre
