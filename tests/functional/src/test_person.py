import pytest


@pytest.mark.asyncio
async def test_get_all_persons(prepare_es_person, make_get_request, get_all_data_elastic):
    """Вывести всех персон"""

    # получаем всех персон из elasticsearch
    all_persons = await get_all_data_elastic('persons')

    response = await make_get_request('/person', {'size': 10000, 'page': 1})

    assert response.status == 200

    assert len(response.body) == len(all_persons)


@pytest.mark.asyncio
async def test_search_detailed(prepare_es_person, make_get_request):
    """Поиск персоны по имени"""

    response = await make_get_request('/person', {'query': 'Test'})

    assert response.status == 200

    assert len(response.body) == 1

    assert response.body == prepare_es_person


@pytest.mark.asyncio
async def test_get_by_id(prepare_es_person, make_get_request):
    """Тест проверяет работу получения по id в эндпоинте person"""

    response = await make_get_request('/person/7f489c61-1a21-43d2-a3ad-3d900f8a9b5e')

    # Проверка результата
    assert response.status == 200

    assert response.body == prepare_es_person[0]


@pytest.mark.asyncio
async def test_get_films_by_peson_id(prepare_es_person, prepare_es_film, make_get_request):
    """Тест проверяет получение фильмов по uuid персоны"""
    film = prepare_es_film[0]
    short_film = {'id': film.get('id'),
                  'title': film.get('title'),
                  'imdb_rating': film.get('imdb_rating')}

    response = await make_get_request('/person/7f489c61-1a21-43d2-a3ad-3d900f8a9b5e/films')

    assert response.status == 200

    assert response.body[0] == short_film


@pytest.mark.asyncio
async def test_validator(make_get_request):
    """Тест корректной валидации форм"""

    response = await make_get_request('/person')
    assert response.status == 200, 'empty parametr validator, status must be 200'

    response = await make_get_request('/person/wrong-uuid')
    assert response.status == 422, 'wrong uuid validator, status must be 422'

    response = await make_get_request('/person', {'page': 101})
    assert response.status == 422, 'too large page validator, status must be 422'

    response = await make_get_request('/person', {'page': 0})
    assert response.status == 422, 'too small page validator, status must be 422'

    response = await make_get_request('/person', {'size': 10001})
    assert response.status == 422, 'too large size validator, status must be 422'

    response = await make_get_request('/person', {'size': 0})
    assert response.status == 422, 'too small size validator, status must be 422'

    response = await make_get_request('/person', {'query': 'PersonNonExists'})
    assert response.status == 404, 'search non-existent person validator, status must be 404'

    # этот запрос сделан без удаления кэша
    response = await make_get_request('/person', {'page': 1, 'size': 10000}, False)
    assert response.status == 200, 'get all persons without delete cache validator, status must be 200'

    # в этом запросе мы получаем результат кэша от первого запроса
    # и сравниваем затраченное время
    response2 = await make_get_request('/person', {'page': 1, 'size': 10000})
    assert response.status == 200, 'get all persons without delete cache, status must be 200'

    assert response.resp_speed > response2.resp_speed
