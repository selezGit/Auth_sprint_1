from flask import Blueprint, request
from app.api.v1.proto.auth_pb2 import LoginRequest
from app.api.v1.proto.connector import connect_server_auth
from flask import jsonify, make_response
from http import HTTPStatus
from flask_restx import Namespace, Resource
from .dto import auth_reqparser, user_model

auth_ns = Namespace(name="auth", validate=True)

auth_ns.models[user_model.name] = user_model

client = connect_server_auth()


@auth_ns.route('/login')
class Login(Resource):
    @auth_ns.expect(auth_reqparser)
    @auth_ns.response(int(HTTPStatus.OK), "Login succeeded.")
    @auth_ns.response(int(HTTPStatus.UNAUTHORIZED), "email or password does not match")
    @auth_ns.response(int(HTTPStatus.BAD_REQUEST), "Validation error.")
    @auth_ns.response(int(HTTPStatus.INTERNAL_SERVER_ERROR), "Internal server error.")
    def get(self):
        login_data = LoginRequest(login='sdf', password='asdf')
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



