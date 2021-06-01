from http import HTTPStatus

from flask import jsonify
from flask_restx import Namespace, Resource

user_ns = Namespace(name='user', validate=True)


@user_ns.route('/', endpoint='user')
class User(Resource):
    def post(self):
        return jsonify(
            status='success',
            message='hello world!',
            token_type='bearer'
        )

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
