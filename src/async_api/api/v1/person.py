from http import HTTPStatus
from typing import List, Optional

from api.v1.base_view import BaseView
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from models.film import FilmShort
from models.person import Person
from pydantic import UUID4
from services.film import FilmService, get_film_service
from services.person import PersonService, get_person_service

router = APIRouter()


class PersonView(BaseView):
    @router.get("/{person_id}", response_model=Person, summary="Персона")
    async def get_details(
            person_id: UUID4,
            request: Request = None,
            person_service: PersonService = Depends(get_person_service),
    ) -> Person:
        """Возвращает информацию по одной персоне"""
        person = await person_service.get_by_id(url=str(request.url), id=str(person_id))
        if not person:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND, detail="person not found"
            )
        return person

    @router.get(
        "/{person_id}/films",
        response_model=List[FilmShort],
        summary="Фильмы с участием персоны",
    )
    async def films_with_person(
            person_id: UUID4,
            size: Optional[int] = Query(default=50, ge=1, le=10000),
            page: Optional[int] = Query(default=1, ge=1, le=100),
            request: Request = None,
            person_service: PersonService = Depends(get_person_service),
            film_service: FilmService = Depends(get_film_service),
    ) -> List[FilmShort]:
        """Возвращает список фильмов в которых участвовал персонаж"""
        # отсекаем окончание запроса для получения валидного кэша
        person_url = "/".join(str(request.url).split("/")[:-1])
        person = await person_service.get_by_id(url=person_url, id=str(person_id))
        if not person:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND, detail="person not found"
            )

        films = await film_service.get_by_list_id(
            url=str(request.url), film_ids=person["film_ids"], page=page, size=size
        )
        if not films:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND, detail="film not found"
            )

        return films

    @router.get("/", response_model=List[Person], summary="Список персон")
    async def get_all(
            query: Optional[str] = None,
            size: Optional[int] = Query(default=50, ge=1, le=10000),
            page: Optional[int] = Query(default=1, ge=1, le=100),
            request: Request = None,
            person_service: PersonService = Depends(get_person_service),
    ):
        """Возвращает информацию
        по одному или нескольким персонам"""

        persons = await person_service.get_by_param(
            url=str(request.url), q=query, page=page, size=size
        )

        if not persons:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND, detail="person not found"
            )

        return persons
