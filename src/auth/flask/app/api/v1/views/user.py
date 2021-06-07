from http import HTTPStatus

from app.api.v1.models.request_model import (auth_register_parser,
                                         change_email_parser,
                                         change_password_parser, 
                                         delete_me_parser)
from app.api.v1.models.response_model import (nested_history_model,
                                          user_create_model,
                                          user_history_model)
from app.api.v1.services.user import (change_email_logic,
                                      change_password_logic, create_user_logic,
                                      delete_user_logic, get_user_logic,
                                      history_logic)
from flask import request
from flask_restx import Namespace, Resource

user_ns = Namespace(name='user', validate=True)
user_ns.models[user_create_model.name] = user_create_model
user_ns.models[nested_history_model.name] = nested_history_model
user_ns.models[user_history_model.name] = user_history_model




@user_ns.route('/', endpoint='user')
class User(Resource):
    @user_ns.expect(auth_register_parser)
    @user_ns.response(int(HTTPStatus.CREATED), "Success", user_create_model)
    @user_ns.response(int(HTTPStatus.CONFLICT), "Email address is already registered.")
    @user_ns.response(int(HTTPStatus.BAD_REQUEST), "Validation error.")
    @user_ns.response(int(HTTPStatus.SERVICE_UNAVAILABLE), "Internal server error.")
    def post(self):
        request_data = auth_register_parser.parse_args()
        login = request_data.get("login")
        email = request_data.get("email")
        password = request_data.get("password")
        return create_user_logic(login=login, email=email, password=password)

    @user_ns.doc(security="access_token")
    @user_ns.expect(delete_me_parser)
    @user_ns.response(int(HTTPStatus.OK), "Success")
    @user_ns.response(int(HTTPStatus.BAD_REQUEST), "Validation error.")
    @user_ns.response(int(HTTPStatus.UNAUTHORIZED), "Token is invalid or expired.")
    @user_ns.response(int(HTTPStatus.SERVICE_UNAVAILABLE), "Internal server error.")
    def delete(self):
        request_data = delete_me_parser.parse_args()
        password = request_data.get('password')
        access_token = request.headers.get('Authorization')
        user_agent = request.headers.get('User-Agent')
        return delete_user_logic(access_token=access_token, user_agent=user_agent, password=password)


@user_ns.route('/me', endpoint='user_me')
class UserMe(Resource):
    @user_ns.doc(security="access_token")
    @user_ns.response(int(HTTPStatus.OK), "Success", user_create_model)
    @user_ns.response(int(HTTPStatus.BAD_REQUEST), "Validation error.")
    @user_ns.response(int(HTTPStatus.UNAUTHORIZED), "Token is invalid or expired.")
    @user_ns.response(int(HTTPStatus.SERVICE_UNAVAILABLE), "Internal server error.")
    def get(self):
        access_token = request.headers.get('Authorization')
        user_agent = request.headers.get('User-Agent')
        return get_user_logic(access_token=access_token, user_agent=user_agent)


@user_ns.route('/change-password', endpoint='user_change_password')
class ChangePassword(Resource):
    @user_ns.doc(security="access_token")
    @user_ns.expect(change_password_parser)
    @user_ns.response(int(HTTPStatus.OK), "password changed successfully")
    @user_ns.response(int(HTTPStatus.BAD_REQUEST), "Validation error.")
    @user_ns.response(int(HTTPStatus.UNAUTHORIZED), "Token is invalid or expired.")
    @user_ns.response(int(HTTPStatus.SERVICE_UNAVAILABLE), "Internal server error.")
    def patch(self):
        request_data = change_password_parser.parse_args()
        old_password = request_data.get("old_password")
        new_password = request_data.get("new_password")
        access_token = request.headers.get('Authorization')
        user_agent = request.headers.get('User-Agent')
        return change_password_logic(old_password=old_password,
                                     new_password=new_password,
                                     access_token=access_token,
                                     user_agent=user_agent)


@user_ns.route('/change-email', endpoint='user_change_email')
class ChangeEmail(Resource):
    @user_ns.doc(security="access_token")
    @user_ns.expect(change_email_parser)
    @user_ns.response(int(HTTPStatus.OK), "email changed successfully")
    @user_ns.response(int(HTTPStatus.BAD_REQUEST), "Validation error.")
    @user_ns.response(int(HTTPStatus.UNAUTHORIZED), "Token is invalid or expired.")
    @user_ns.response(int(HTTPStatus.SERVICE_UNAVAILABLE), "Internal server error.")
    def patch(self):
        request_data = change_email_parser.parse_args()
        password = request_data.get("password")
        email = request_data.get("email")
        access_token = request.headers.get('Authorization')
        user_agent = request.headers.get('User-Agent')
        return change_email_logic(password=password,
                                  email=email,
                                  access_token=access_token,
                                  user_agent=user_agent)


@user_ns.route('/history', endpoint='user_history')
class History(Resource):
    @user_ns.doc(security="access_token")
    @user_ns.response(int(HTTPStatus.OK), "user successfully deleted.", user_history_model)
    @user_ns.response(int(HTTPStatus.BAD_REQUEST), "Validation error.")
    @user_ns.response(int(HTTPStatus.UNAUTHORIZED), "Token is invalid or expired.")
    @user_ns.response(int(HTTPStatus.SERVICE_UNAVAILABLE), "Internal server error.")
    def get(self):
        access_token = request.headers.get('Authorization')
        user_agent = request.headers.get('User-Agent')
        return history_logic(access_token=access_token, user_agent=user_agent)
