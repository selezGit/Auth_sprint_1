import json
from http import HTTPStatus
import re

import grpc
from app.api.v1.exceptions import error_handler
from app.api.v1.proto.auth_pb2 import (UserCreateRequest, UserDeleteMe,
                                       UserGetRequest, UserHistoryRequest,
                                       UserUpdateEmailRequest,
                                       UserUpdatePasswordRequest)
from app.api.v1.proto.connector import ConnectServerGRPC
from flask import jsonify
from google.protobuf.json_format import MessageToDict


client = ConnectServerGRPC().conn_user()


def create_user_logic(login: str, email: str, password: str):
    create_user_data = UserCreateRequest(
            login=login, email=email, password=password)
    try:
        request = MessageToDict(client.Create(create_user_data))
        response = jsonify(request)
        response.status_code = HTTPStatus.CREATED

        return response

    except grpc.RpcError as rpc_error:
        return error_handler.get_response(status=rpc_error.code(),
                                          details=rpc_error.details())


def delete_user_logic(access_token: str, user_agent: str):
    delete_user_data = UserDeleteMe(access_token, user_agent)
    try:
        request = client.DeleteMe(delete_user_data)
        # TODO логика удаления не работает, выкидывает ошибку
        return jsonify(message='user successfully deleted')

    except grpc.RpcError as rpc_error:
        return error_handler.get_response(status=rpc_error.code(),
                                          details=rpc_error.details())


def get_user_logic(access_token: str, user_agent: str):
    get_user_data = UserGetRequest(
            access_token=access_token, user_agent=user_agent)
    try:
        request = MessageToDict(client.Get(get_user_data))
        return jsonify(request)

    except grpc.RpcError as rpc_error:
        return error_handler.get_response(status=rpc_error.code(),
                                          details=rpc_error.details())


def history_logic(access_token: str, user_agent: str):
    history_data = UserHistoryRequest(
            access_token=access_token, user_agent=user_agent)
    try:
        request = MessageToDict(client.GetHistory(history_data))
        return jsonify(request)

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
