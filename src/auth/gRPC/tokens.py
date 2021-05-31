import datetime

import jwt
import os
from db.no_sql_db import del_refresh_token, save_refresh_token, add_to_blacklist
from typing import Any

SECRET_KEY = os.getenv('SECRET_KEY', 'somesecret')


def create_access_token(data: dict) -> str:
    """Функция создаёт access jwt токен"""
    return jwt.encode(data, SECRET_KEY, algorithm='HS256')


def create_refresh_token(data: dict, access_token: str) -> str:
    """Функция создаёт refresh jwt токен
    я решил в качестве секретного ключа использовать access_token+secret_key
    что бы удостовериться, что refresh token привязан к определённому access токену """
    return jwt.encode(data, access_token+SECRET_KEY, algorithm='HS256')


def decode_token(token: str, key: str) -> dict:
    """Функция декодирует токен"""
    try:
        data = jwt.decode(token, key, algorithm='HS256')
    except:
        data = {}
    return data


def generate_new_tokens(data: dict) -> dict:
    """Функция создаёт новую пару токенов"""
    data['exp'] = datetime.datetime.utcnow() + datetime.timedelta(seconds=900)

    access_token = create_access_token(data, SECRET_KEY)
    refresh_token = create_refresh_token(data, access_token, SECRET_KEY)
    # сохраняем refresh_token в redis
    save_refresh_token(refresh_token)

    return {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'expires_in': data['exp'],
        'token_type': 'bearer'
    }


def republish_refresh_token(access_token: str, refresh_token: str) -> Any:
    """Функция перевыдаёт новую пару access и refresh токенов
    в случае если refresh токен валидный и ни разу не был использован"""
    data = decode_token(refresh_token, access_token+SECRET_KEY)
    # проверяем валидность токена и достаём из него информацию о пользователе
    if data:
        # токен валидный, но необходимо проверить его наличие в redis
        if del_refresh_token(refresh_token):
            # если вернулся ответ, что токен есть в redis, то перевыдаём новые токены
            return generate_new_tokens(data, SECRET_KEY)

    return 'Refresh token is not valid'


def logout_access_token(access_token: str) -> None:
    """Задача данной функции, занести access_token с 
    неистёкшим скроком годности в чёрный список redis"""
    data = decode_token(access_token, SECRET_KEY)

    if data:
        add_to_blacklist(access_token, data['exp'])
