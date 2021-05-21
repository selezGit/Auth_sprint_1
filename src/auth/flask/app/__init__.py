from flask import Flask
from .config import DevelopmentConfig

def create_app():
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_object(DevelopmentConfig)
    from .views import auth, user

    app.register_blueprint(auth.bp)
    app.register_blueprint(user.bp)

    return app