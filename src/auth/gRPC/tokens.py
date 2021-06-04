import datetime
import os
from typing import Any

import jwt

from db.no_sql_db import add_to_blacklist, del_refresh_token, save_refresh_token


class Token:
    def _create_refresh_token(self, data: dict, access_token: str) -> str:
        """Функция создаёт refresh jwt токен
        я решил в качестве секретного ключа использовать access_token+secret_key
        что бы удостовериться, что refresh token привязан к определённому access токену"""
        return jwt.encode(data, access_token + self.SECRET_KEY, algorithm="HS256")

    def _decode_token(self, token: str, key: str) -> dict:
        """Функция декодирует токен"""
        try:
            data = jwt.decode(token, key, algorithm="HS256")
        except:
            data = {}
        return data

    def generate_new_tokens(self, data: dict) -> dict:
        """Функция создаёт новую пару токенов"""
        data["exp"] = datetime.datetime.utcnow() + datetime.timedelta(seconds=900)

        access_token = self._create_access_token(data, self.SECRET_KEY)
        refresh_token = self._create_refresh_token(data, access_token, self.SECRET_KEY)
        # сохраняем refresh_token в redis
        save_refresh_token(refresh_token)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_in": data["exp"],
            "token_type": "bearer",
        }

    def republish_refresh_token(self, access_token: str, refresh_token: str) -> Any:
        """Функция перевыдаёт новую пару access и refresh токенов
        в случае если refresh токен валидный и ни разу не был использован"""
        data = self._decode_token(refresh_token, access_token + self.SECRET_KEY)
        # проверяем валидность токена и достаём из него информацию о пользователе
        if data:
            # токен валидный, но необходимо проверить его наличие в redis
            if del_refresh_token(refresh_token):
                # если вернулся ответ, что токен есть в redis, то перевыдаём новые токены
                return self.generate_new_tokens(data, self.SECRET_KEY)

        return "Refresh token is not valid"

    def logout_access_token(self, access_token: str) -> None:
        """Задача данной функции, занести access_token с
        неистёкшим cроком годности в чёрный список redis
        реализация обсуждаема, суть тут
        https://medium.com/devgorilla/how-to-log-out-when-using-jwt-a8c7823e8a6"""
        data = self._decode_token(access_token, self.SECRET_KEY)

        if data:
            add_to_blacklist(access_token, data["exp"])
