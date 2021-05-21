# Функциональные тесты

## Запуск

Для запуска тестов подходят следующие команды:

Билд + запуск со своим окружением:

    $ sudo docker-compose -f docker-compose.yml  up -d --build

Только запуск тестов:

    $ sudo docker-compose up tests

Остановка:

    $ sudo docker-compose -f docker-compose.yml down
   
