from http import HTTPStatus

from flask.json import jsonify

from app.api.v1.models.request_model import auth_login_parser
from app.api.v1.models.response_model import auth_login_model
from app.api.v1.services.auth import (login_logic, logout_logic, refresh_logic,
                                      test_logic)
from flask import request
from flask_restx import Namespace, Resource

auth_ns = Namespace(name='auth', validate=True)
auth_ns.models[auth_login_model.name] = auth_login_model


@auth_ns.route('/login', endpoint='auth_login')
class Login(Resource):
    @auth_ns.expect(auth_login_parser)
    @auth_ns.response(int(HTTPStatus.OK), 'Success', auth_login_model)
    @auth_ns.response(int(HTTPStatus.UNAUTHORIZED), 'email or password does not match')
    @auth_ns.response(int(HTTPStatus.BAD_REQUEST), 'Validation error.')
    @auth_ns.response(int(HTTPStatus.SERVICE_UNAVAILABLE), 'Internal server error.')
    def post(self):
        request_data = auth_login_parser.parse_args()
        login = request_data.get('login')
        password = request_data.get('password')
        user_agent = request.headers.get('User-Agent')
        return login_logic(login=login,
                           password=password,
                           user_agent=user_agent)
                           
# @auth_ns.route('/login_via_SN', endpoint='auth_login_via_SN')
# class LoginViaSN(Resource):
#     @auth_ns.response(int(HTTPStatus.OK), 'Success')
#     @auth_ns.response(int(HTTPStatus.UNAUTHORIZED), 'email or password does not match')
#     @auth_ns.response(int(HTTPStatus.BAD_REQUEST), 'Validation error.')
#     @auth_ns.response(int(HTTPStatus.SERVICE_UNAVAILABLE), 'Internal server error.')
#     def post(self):
#         return jsonify(hello='world')



@auth_ns.route('/refresh', endpoint='auth_refresh')
class Refresh(Resource):
    @auth_ns.doc(security='refresh_token')
    @auth_ns.response(int(HTTPStatus.OK), 'Success', auth_login_model)
    @auth_ns.response(int(HTTPStatus.UNAUTHORIZED), 'Token is invalid or expired.')
    @auth_ns.response(int(HTTPStatus.SERVICE_UNAVAILABLE), 'Internal server error.')
    def post(self):
        refresh_token = request.headers.get('Authorization')
        user_agent = request.headers.get('User-Agent')
        return refresh_logic(refresh_token=refresh_token,
                             user_agent=user_agent)


@ auth_ns.route('/logout', endpoint='auth_logout')
class Logout(Resource):
    @auth_ns.doc(security='access_token')
    @auth_ns.response(int(HTTPStatus.OK), 'Log out succeeded, token is no longer valid.')
    @auth_ns.response(int(HTTPStatus.UNAUTHORIZED), 'Token is invalid or expired.')
    @auth_ns.response(int(HTTPStatus.SERVICE_UNAVAILABLE), 'Internal server error.')
    def post(self):
        access_token = request.headers.get('Authorization')
        user_agent = request.headers.get('User-Agent')
        return logout_logic(access_token=access_token,
                            user_agent=user_agent)


@auth_ns.route('/test-token', endpoint='auth_test_token')
class TestToken(Resource):
    @auth_ns.doc(security='access_token')
    @auth_ns.response(int(HTTPStatus.OK), 'Token is valid')
    @auth_ns.response(int(HTTPStatus.UNAUTHORIZED), 'Token is invalid or expired.')
    @auth_ns.response(int(HTTPStatus.SERVICE_UNAVAILABLE), 'Internal server error.')
    def get(self):
        access_token = request.headers.get('Authorization')
        user_agent = request.headers.get('User-Agent')
        return test_logic(access_token=access_token,
                          user_agent=user_agent)
