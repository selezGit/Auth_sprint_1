from model.db import db
from model.db_models import User

# Insert-запросы
admin = User('admin', 'password')
db.session.add(admin)
db.session.commit()

# Select-запросы
User.query.all()
User.query.filter_by(login='admin').first()


# python shell
from db import redis_db


redis_db.get('key')  # Получить значение по ключу
redis_db.set('key', 'value')  # Положить значение по ключу
redis_db.expire('key', 10)  # Установить время жизни ключа в секундах
# А можно последние две операции сделать за один запрос к Redis.
redis_db.setex('key', 10, 'value')  # Положить значение по ключу с ограничением времени жизни в секундах

# python shell
import redis
from db import redis_db


pipeline = redis_db.pipeline()
pipeline.setex('key', 10, 'value')
pipeline.setex('key2', 10, 'value')
pipeline.execute()

# python shell
import redis
from db import redis_db


def set_two_factor_auth_code(pipeline: redis.client.Pipeline) -> None:
    pipeline.setex('key', 10, 'value')
    pipeline.setex('key2', 10, 'value')
    pipeline.setex('key3', 10, 'value')
    pipeline.setex('key4', 10, 'value')

redis_db.transaction(set_two_factor_auth_code)