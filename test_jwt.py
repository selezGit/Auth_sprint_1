import jwt
import datetime


# encode_token({"exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=30)}, key)
def encode_token(data: dict, secret_key: str) -> jwt.encode:
    """Функция создаёт jwt токен"""
    return jwt.encode(data, secret_key, algorithm="HS256")

# decode_token('eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE2MjI0MjI5MTR9.eipw-BGUcujaGDSpsuqnhds8Oq9onAeSAcvfQieoJkw', key)
def decode_token(token: str, key: str) -> dict:
    """Функция декодирует токен и проверяет его валидность"""
    try:
        data = jwt.decode(token, key, algorithms='HS256')
    except:
        data = []
    return data
