from http import HTTPStatus
from flask.globals import request

import grpc
from app.api.v1.exceptions import error_handler
from app.api.v1.proto.auth_pb2 import LoginRequest, LogoutRequest, RefreshTokenRequest, TestTokenRequest
from app.api.v1.proto.connector import ConnectServerGRPC
from flask import jsonify

client = ConnectServerGRPC().conn_auth()


def login_logic(login: str, password: str, user_agent: str):

    login_data = LoginRequest(
        login=login, password=password, user_agent=user_agent)

    try:
        response = client.Login(login_data)
        response = jsonify(
            status='success',
            access_token=response.access_token,
            refresh_token=response.refresh_token,
            token_type=response.token_type,
            expires_in=response.expires_in)
        response.status_code = HTTPStatus.OK
        return response

    except grpc.RpcError as rpc_error:
        return error_handler.get_response(status=rpc_error.code(),
                                          details=rpc_error.details())


def logout_logic(access_token: str, user_agent: str):
    try:
        client.Logout(LogoutRequest(
            access_token=access_token, user_agent=user_agent))

        response = jsonify(
            status='success',
            message='Log out succeeded, token is no longer valid'
        )
        response.status_code = HTTPStatus.OK
        return response

    except grpc.RpcError as rpc_error:
        return error_handler.get_response(status=rpc_error.code(),
                                          details=rpc_error.details())


def refresh_logic(refresh_token: str,
                  user_agent: str):
    try:
        request = client.RefreshToken(RefreshTokenRequest(refresh_token=refresh_token,
                                                          user_agent=user_agent))
        response = jsonify(
            status='success',
            access_token=request.access_token,
            refresh_token=request.refresh_token,
            token_type=request.token_type,
            expires_in=request.expires_in)
        response.status_code = HTTPStatus.OK
        return response
    except grpc.RpcError as rpc_error:
        return error_handler.get_response(status=rpc_error.code(),
                                          details=rpc_error.details())


def test_logic(access_token: str,
               user_agent: str):
    try:
        request = client.TestToken(TestTokenRequest(access_token=access_token,
                                                    user_agent=user_agent))
        print(request)
        response = jsonify(
            status='Token valid',
        )
        response.status_code = HTTPStatus.OK
        # TODO не работает
        return response
    except grpc.RpcError as rpc_error:
        return error_handler.get_response(status=rpc_error.code(),
                                          details=rpc_error.details())
