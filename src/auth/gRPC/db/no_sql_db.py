from db.db import redis_db


def add_refresh_token(refresh_token: str, exp: int = 604800) -> None:
    """Функция сохранения refresh_token в базу по умолчанию задано значение в 7 дней"""
    redis_db.setex(name=refresh_token, time=exp, value='refresh_token')


def del_refresh_token(refresh_token: str) -> bool:
    """Функция удаления refresh_token из redis"""
    if redis_db.exists(refresh_token):
        redis_db.delete(refresh_token)
        return True
    return False


def add_to_blacklist(access_token: str, exp: int) -> None:
    """Функция добавляет access_token в чёрный список """
    redis_db.setex(name=access_token, time=exp, value='black_list')


def check_blacklist(access_token: str) -> bool:
    """Проверяет, находится ли access_token  в чёрном списке """
    return redis_db.exists(access_token)
