from flask import Flask
from .config import DevelopmentConfig
from flask_cors import CORS
import grpc

cors = CORS()


def create_app():
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_object(DevelopmentConfig)
    from .api.v1 import api_bp

    app.register_blueprint(api_bp)
    cors.init_app(app)
    return app


