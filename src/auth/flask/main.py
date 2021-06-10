from app import create_app
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = create_app()
limiter = Limiter(app, key_func=get_remote_address)

if __name__ == '__main__':
    app.run()
