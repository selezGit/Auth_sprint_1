import redis
import os

REDIS_HOST = os.getenv('REDIS_HOST', 'redis-auth') 
REDIS_PORT = os.getenv('REDIS_PORT', 6380)

redis_db = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)



def add_refresh_token(refresh_token: str, exp: int = 604800) -> None:
    """Функция сохранения refresh_token в базу по умолчанию задано значение в 7 дней"""
    redis_db.setex(name=refresh_token, time=exp, value='refresh_token')

def del_refresh_token(refresh_token: str) -> bool:
    """Функция удаления токена из redis"""
    token = redis_db.get(refresh_token, None)

    if token:
        redis_db.delete(refresh_token)
        return True
    return False

def add_to_blacklist(access_token: str, exp: int) -> None:
    """Функция добавляет в чёрный список access_token"""
    redis_db.setex(name=access_token, time=exp, value='black_list')