### Описать методы для модуля gRPC для User.

/user (create)
* Регистрация нового пользователя.
* Хэширование пароля и запись данных в БД.

/user (delete)
* Удаление аккаунта пользователя.

/user/me
* Выдача информации о пользователе.

/user/change-password
* Смена пароля.
* Захешировать новый пароль в базу.

/user/change-email
* Смена e-mail.

/uset/history
* Выдача истории авторизаций пользователя.

Оценка: overkill