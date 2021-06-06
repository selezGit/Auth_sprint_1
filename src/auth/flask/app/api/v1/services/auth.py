import grpc
from app.api.v1.exceptions import error_handler
from app.api.v1.proto.auth_pb2 import (LoginRequest, LogoutRequest,
                                       RefreshTokenRequest, TestTokenRequest)
from app.api.v1.proto.connector import ConnectServerGRPC
from flask import jsonify
from google.protobuf.json_format import MessageToDict

client = ConnectServerGRPC().conn_auth()


def login_logic(login: str, password: str, user_agent: str):

    login_data = LoginRequest(
        login=login, password=password, user_agent=user_agent)

    try:
        request = MessageToDict(client.Login(login_data))
        return jsonify(request)

    except grpc.RpcError as rpc_error:
        return error_handler.get_response(status=rpc_error.code(),
                                          details=rpc_error.details())


def logout_logic(access_token: str, user_agent: str):
    logout_data = LogoutRequest(
        access_token=access_token, user_agent=user_agent)
    try:
        client.Logout(logout_data)

        response = jsonify(
            status='success',
            message='Log out succeeded, token is no longer valid'
        )
        return response

    except grpc.RpcError as rpc_error:
        return error_handler.get_response(status=rpc_error.code(),
                                          details=rpc_error.details())


def refresh_logic(refresh_token: str, user_agent: str):
    refresh_data = RefreshTokenRequest(refresh_token=refresh_token,
                                       user_agent=user_agent)
    try:
        request = MessageToDict(client.RefreshToken(refresh_data))
        return jsonify(request)

    except grpc.RpcError as rpc_error:
        return error_handler.get_response(status=rpc_error.code(),
                                          details=rpc_error.details())


def test_logic(access_token: str, user_agent: str):
    test_token_data = (TestTokenRequest(access_token=access_token,
                                        user_agent=user_agent))
    try:
        request = client.TestToken(test_token_data)
        # TODO не работает
        return jsonify(status='Token is valid')

    except grpc.RpcError as rpc_error:
        return error_handler.get_response(status=rpc_error.code(),
                                          details=rpc_error.details())
