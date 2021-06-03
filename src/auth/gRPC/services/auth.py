import auth_pb2_grpc
from concurrent import futures
import grpc

import crud
from utils.token import create_access_token, create_refresh_token
from auth_pb2 import LoginRequest, LoginResponse
from db.db import db_session as db
from loguru import logger


class AuthService(auth_pb2_grpc.AuthServicer):
    def Login(self, request: LoginRequest, context):
        if request.login is None:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('login field required!')
            return LoginResponse()
        if request.password is None:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('password field required!')
            return LoginResponse()
        if request.user_agent is None:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('user_agent field required!')
            return LoginResponse()
        user = crud.user.get_by(db=db, login=request.login)
        if user is None:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"user with login: {request.login} not found!")
            return LoginResponse()
        try:
            if not crud.user.check_password(user=user, password=request.password):
                context.set_code(grpc.StatusCode.UNAUTHENTICATED)
                context.set_details(f"password not valid!")
                return LoginResponse()

            payload = {
                "user_id": str(user.id),
                "agent": request.user_agent
            }

            now, expire, access_token = create_access_token(payload=payload)
            now, expire, refresh_token = create_refresh_token(payload=payload)
        except Exception as e:
            logger.debug(e)
            return LoginResponse()

        return LoginResponse(access_token=access_token, refresh_token=refresh_token, expires_in=expire,
                             token_type="Barear")
