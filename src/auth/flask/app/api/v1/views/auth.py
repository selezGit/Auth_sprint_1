from http import HTTPStatus

from app.api.v1.db.request_model import auth_loginparser, user_model
from app.api.v1.proto.auth_pb2 import LoginRequest
from app.api.v1.proto.connector import ConnectServerGRPC
from flask import Blueprint, jsonify, make_response, request
from flask_restx import Namespace, Resource

auth_ns = Namespace(name="auth", validate=True)

auth_ns.models[user_model.name] = user_model

client = ConnectServerGRPC().conn_auth()


@auth_ns.route('/login', endpoint="auth_login")
class Login(Resource):
    @auth_ns.expect(auth_loginparser)
    @auth_ns.response(int(HTTPStatus.OK), "Login succeeded.")
    @auth_ns.response(int(HTTPStatus.UNAUTHORIZED), "email or password does not match")
    @auth_ns.response(int(HTTPStatus.BAD_REQUEST), "Validation error.")
    @auth_ns.response(int(HTTPStatus.INTERNAL_SERVER_ERROR), "Internal server error.")
    def post(self):
        request_data = auth_loginparser.parse_args()
        login = request_data.get("login")
        password = request_data.get("password")

        login_data = LoginRequest(login=login, password=password)
        response = client.Login(login_data)
        print(response)
        return jsonify(
            status='success',
            message='hello world',
            token_type='bearer'
        )


@auth_ns.route('/refresh', endpoint='auth_refresh')
class Refresh(Resource):
    def post(self):
        return jsonify(
            status='success',
            message='hello world',
            token_type='bearer'
        )


@auth_ns.route('/logout', endpoint='auth_logout')
class Logout(Resource):
    def post(self):
        return jsonify(
            status='success',
            message='hello world',
            token_type='bearer'
        )


@auth_ns.route('/test-token', endpoint='auth_test_token')
class TestToken(Resource):
    def get(self):
        return jsonify(
            status='success',
            message='hello world!',
            token_type='bearer'
        )
