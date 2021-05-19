import pytest


@pytest.mark.asyncio
async def test_get_all_films(prepare_es_film, make_get_request, get_all_data_elastic):
    """Вывести все фильмы"""

    # получаем все фильмы из elasticsearch
    all_films = await get_all_data_elastic('movies')

    response = await make_get_request('/film', {'size': 10000, 'page': 1})

    assert response.status == 200

    assert len(response.body) == len(all_films)


@pytest.mark.asyncio
async def test_search_detailed(prepare_es_film, make_get_request):
    """Поиск конкретного фильма"""

    # Выполнение запроса
    response = await make_get_request('/film', {'query': 'abracadabra'})
    # Проверка результата
    assert response.status == 200

    assert len(response.body) == 1

    assert response.body == prepare_es_film


@pytest.mark.asyncio
async def test_get_by_id(prepare_es_film, make_get_request):
    """Тест проверяет работу получения по id в эндпоинте film"""

    response = await make_get_request('/film/3a5f9a83-4b74-48be-a44e-a6c8beee9460')

    # Проверка результата
    assert response.status == 200

    assert response.body == prepare_es_film[0]


@pytest.mark.asyncio
async def test_validator(make_get_request):
    """Тест корректной валидации форм"""

    response = await make_get_request('/film')
    assert response.status == 200, 'empty parametr validator, status must be 200'

    response = await make_get_request('/film/wrong-uuid')
    assert response.status == 422, 'wrong uuid validator, status must be 422'

    response = await make_get_request('/film', {'genre': 'wrong-uuid'})
    assert response.status == 422, 'wrong genre uuid validator, status must be 422'

    response = await make_get_request('/film', {'page': 101})
    assert response.status == 422, 'too large page validator, status must be 422'

    response = await make_get_request('/film', {'page': 0})
    assert response.status == 422, 'too small page validator, status must be 422'

    response = await make_get_request('/film', {'size': 10001})
    assert response.status == 422, 'too large size validator, status must be 422'

    response = await make_get_request('/film', {'size': 0})
    assert response.status == 422, 'too small size validator, status must be 422'

    response = await make_get_request('/film', {'query': 'MovieNonExists'})
    assert response.status == 404, 'search non-existent movie validator, status must be 404'

    # этот запрос сделан без удаления кэша
    response = await make_get_request('/film', {'page': 1, 'size': 10000}, False)
    assert response.status == 200, 'get all movies without delete cache validator, status must be 200'

    # в этом запросе мы получаем результат кэша от первого запроса
    # и сравниваем затраченное время
    response2 = await make_get_request('/film', {'page': 1, 'size': 10000})
    assert response.status == 200, 'get all movies without delete cache validator, status must be 200'

    assert response.resp_speed > response2.resp_speed
