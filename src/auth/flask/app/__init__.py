from flask import Flask
from .config import DevelopmentConfig
from flask_cors import CORS
from app.proto.auth_pb2_grpc import AuthStub
import grpc
from .db import init_db


def create_app():
    init_db()
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_object(DevelopmentConfig)
    from .views import auth, user

    app.register_blueprint(auth.bp)
    app.register_blueprint(user.bp)

    CORS(app)
    return app


def connect_server_auth():
    channel = grpc.insecure_channel("server-auth:50051")
    client = AuthStub(channel)
    return client

client = connect_server_auth()