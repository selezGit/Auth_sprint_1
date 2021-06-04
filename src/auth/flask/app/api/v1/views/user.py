from http import HTTPStatus

from app.api.v1.db.request_model import auth_reqparser, user_model
from app.api.v1.proto.auth_pb2 import UserCreateRequest
from app.api.v1.proto.connector import ConnectServerGRPC
from flask import jsonify
from flask_restx import Namespace, Resource

user_ns = Namespace(name='user', validate=True)
user_ns.models[user_model.name] = user_model


client = ConnectServerGRPC().conn_user()


@user_ns.route('/', endpoint='user')
class User(Resource):
    @user_ns.expect(auth_reqparser)
    @user_ns.response(int(HTTPStatus.CREATED), "New user was successfully created.")
    @user_ns.response(int(HTTPStatus.CONFLICT), "Email address is already registered.")
    @user_ns.response(int(HTTPStatus.BAD_REQUEST), "Validation error.")
    @user_ns.response(int(HTTPStatus.INTERNAL_SERVER_ERROR), "Internal server error.")
    def post(self):
        request_data = auth_reqparser.parse_args()
        login = request_data.get("login")
        email = request_data.get("email")
        password = request_data.get("password")
        registration_data = UserCreateRequest(
            login=login, email=email, password=password)
        response = client.Create(registration_data)

        print(response)
        response = jsonify(status='Success')
        response.status_code = 201
        return response

    def delete(self):
        return jsonify(
            status='success',
            message='hello world!',
            token_type='bearer'
        )


@user_ns.route('/me', endpoint='user_me')
class UserMe(Resource):
    def get(self):
        return jsonify(
            status='success',
            message='hello world!',
            token_type='bearer'
        )


@user_ns.route('/change-password', endpoint='user_change_password')
class ChangePassword(Resource):
    def patch(self):
        return jsonify(
            status='success',
            message='hello world!',
            token_type='bearer'
        )


@user_ns.route('/change-email', endpoint='user_change_email')
class ChangeEmail(Resource):
    def patch(self):
        return jsonify(
            status='success',
            message='hello world!',
            token_type='bearer'
        )


@user_ns.route('/history', endpoint='user_history')
class ChangeEmail(Resource):
    def get(self):
        return jsonify(
            status='success',
            message='hello world!',
            token_type='bearer'
        )
