from http import HTTPStatus

from flask import jsonify
from flask_restx import Namespace, Resource
from .dto import auth_reqparser, user_model

user_ns = Namespace(name='user', validate=True)
# user_ns.models[user_model.name] = user_model

@user_ns.route('/', endpoint='user')
class User(Resource):
    @user_ns.expect(auth_reqparser)
    @user_ns.response(int(HTTPStatus.CREATED), "New user was successfully created.")
    @user_ns.response(int(HTTPStatus.CONFLICT), "Email address is already registered.")
    @user_ns.response(int(HTTPStatus.BAD_REQUEST), "Validation error.")
    @user_ns.response(int(HTTPStatus.INTERNAL_SERVER_ERROR), "Internal server error.")
    def post(self):
        request_data = auth_reqparser.parse_args()
        email = request_data.get("email")
        password = request_data.get("password")
        response = jsonify(
            status='success',
            message='hello world!',
            token_type='bearer'
        )

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
