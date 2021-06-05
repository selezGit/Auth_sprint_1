import json
from http import HTTPStatus

import grpc
from app.api.v1.exceptions import error_handler
from app.api.v1.proto.auth_pb2 import (UserCreateRequest, UserDeleteMe,
                                       UserGetRequest, UserHistoryRequest,
                                       UserUpdateEmailRequest,
                                       UserUpdatePasswordRequest)
from app.api.v1.proto.connector import ConnectServerGRPC
from flask import jsonify
from flask.globals import request

client = ConnectServerGRPC().conn_user()


def create_user_logic(login: str, email: str, password: str):
    try:
        request = client.Create(UserCreateRequest(
            login=login, email=email, password=password))
        response = jsonify(status='Success',
                           user_id=request.id,
                           login=request.login,
                           email=request.email)
        response.status_code = HTTPStatus.CREATED
        return response

    except grpc.RpcError as rpc_error:
        return error_handler.get_response(status=rpc_error.code(),
                                          details=rpc_error.details())


def delete_user_logic(access_token: str, user_agent: str):
    try:
        request = client.DeleteMe(UserDeleteMe(access_token, user_agent))
        response = jsonify(status='Success',
                           message='user successfully deleted')
        response.status_code = HTTPStatus.OK
        # TODO логика удаления не работает, выкидывает ошибку
        return response
    except grpc.RpcError as rpc_error:
        return error_handler.get_response(status=rpc_error.code(),
                                          details=rpc_error.details())


def get_user_logic(access_token: str, user_agent: str):
    try:
        request = client.Get(UserGetRequest(
            access_token=access_token, user_agent=user_agent))
        print(request)
        response = jsonify(status='Success',
                           user_id=request.id,
                           login=request.login,
                           email=request.email)
        response.status_code = HTTPStatus.OK
        return response
    except grpc.RpcError as rpc_error:
        return error_handler.get_response(status=rpc_error.code(),
                                          details=rpc_error.details())


def history_logic(access_token: str, user_agent: str):
    try:

        request = client.GetHistory(UserHistoryRequest(
            access_token=access_token, user_agent=user_agent))
        response = jsonify(status='Success')
        response.status_code = HTTPStatus.OK

        # TODO тут не понятно как возвращать данные, они в неизвестном мне формате
        return request.rows

    except grpc.RpcError as rpc_error:
        return error_handler.get_response(status=rpc_error.code(),
                                          details=rpc_error.details())


def change_password_logic(old_password: str,
                          new_password: str,
                          access_token: str,
                          user_agent: str):
    try:
        request = client.UpdatePassword(UserUpdatePasswordRequest(old_password=old_password,
                                                                  new_password=new_password,
                                                                  access_token=access_token,
                                                                  user_agent=user_agent))
        print(request)
        response = jsonify(status='Success')
        response.status_code = HTTPStatus.OK
        # TODO не работает
        return response

    except grpc.RpcError as rpc_error:
        return error_handler.get_response(status=rpc_error.code(),
                                          details=rpc_error.details())


def change_email_logic(password: str,
                       email: str,
                       access_token: str,
                       user_agent: str):
    try:
        request = client.UpdateEmail(UserUpdateEmailRequest(password=password,
                                                            email=email,
                                                            access_token=access_token,
                                                            user_agent=user_agent))
        print(request)
        response = jsonify(status='Success')
        response.status_code = HTTPStatus.OK
        # TODO не работает

        return response
    except grpc.RpcError as rpc_error:
        return error_handler.get_response(status=rpc_error.code(),
                                          details=rpc_error.details())
