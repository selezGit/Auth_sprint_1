import auth_pb2_grpc
from auth_pb2 import LoginResponse, UserResponse, UserCreateRequest, UserGetRequest
import grpc
from db.db import db_session as db
import crud
from pathlib import Path
from loguru import logger


class UserService(auth_pb2_grpc.UserServicer):
    def Create(self, request: UserCreateRequest, context) -> UserResponse:
        if request.login is None:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('login field required!')
            return UserResponse()
        if request.password is None:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('password field required!')
            return UserResponse()
        if request.email is None:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('email field required!')
            return UserResponse()
        logger.debug('User validation!')
        try:
            user = crud.user.create(db=db, obj_in={
                "login": request.login,
                "email": request.email,
                "password": request.password
            })
        except Exception as e:
            context.set_code(grpc.StatusCode.WARNING)
            context.set_details(e)
            logger.exception(e)
            return UserResponse()
        logger.debug('User created!')
        return UserResponse(id=str(user.id), login=user.login, email=user.email)

    def Get(self, request: UserGetRequest, context):
        pass
