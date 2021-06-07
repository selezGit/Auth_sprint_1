from db.db import redis_db


def add_refresh_token(refresh_token: str, exp) -> None:
    """Функция сохранения refresh_token в базу по умолчанию задано значение в 7 дней"""
    name = f"white_list:{refresh_token}"
    redis_db.setex(name=name, time=exp, value='refresh_token')


def check_whitelist(refresh_token: str) -> bool:
    """проверка refresh token"""
    name = f"white_list:{refresh_token}"
    return redis_db.exists(name)


def del_refresh_token(refresh_token: str) -> bool:
    """Функция удаления refresh_token из redis"""
    name = f"white_list:{refresh_token}"
    if redis_db.exists(name):
        redis_db.delete(name)
        return True
    return False


def add_to_blacklist(access_token: str, exp) -> None:
    """Функция добавляет access_token в чёрный список """
    name = f"black_list:{access_token}"
    redis_db.setex(name=name, time=exp, value='black_list')


def check_blacklist(access_token: str) -> bool:
    """Проверяет, находится ли access_token  в чёрном списке """
    name = f"black_list:{access_token}"
    return redis_db.exists(name)


def add_auth_user(user_id: str, user_agent: str, refresh_token: str, exp):
    name = f"auth:{user_id}"
    redis_db.hset(name, user_agent, refresh_token)
    redis_db.expire(name, exp)


def get_all_auth_user(user_id: str):
    name = f"auth:{user_id}"
    return redis_db.hgetall(name)


def get_auth_user(user_id: str, user_agent: str):
    name = f"auth:{user_id}"
    return redis_db.hget(name, user_agent)


def del_auth_user(user_id: str, user_agent: str):
    name = f"auth:{user_id}"
    return redis_db.hdel(name, user_agent)


def del_all_auth_user(user_id: str):
    name = f"auth:{user_id}"
    return redis_db.delete(name)
