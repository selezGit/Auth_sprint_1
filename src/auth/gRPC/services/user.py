import auth_pb2_grpc
from auth_pb2 import UserResponse, UserCreateRequest, UserGetRequest, UserHistoryResponse, UserHistory,UserHistoryRequest
import grpc
from db.db import get_db
import crud
from pathlib import Path
from loguru import logger
from utils.token import decode_token, check_expire


class UserService(auth_pb2_grpc.UserServicer):
    def Create(self, request: UserCreateRequest, context) -> UserResponse:
        db = next(get_db())
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
            logger.exception(e)
            context.set_code(grpc.StatusCode.WARNING)
            context.set_details(e)
            return UserResponse()
        logger.debug('User created!')
        user_response = UserResponse(id=str(user.id), login=user.login, email=user.email)
        return user_response

    def Get(self, request: UserGetRequest, context):
        db = next(get_db())
        if request.access_token is None:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('access_token field required!')
            return UserResponse()
        if request.user_agent is None:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('user_agent field required!')
            return UserResponse()
        access_token = request.access_token
        user_agent = request.user_agent
        payload = decode_token(token=access_token)
        if not check_expire(payload['expire']):
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details('access_token not valid!')
            return UserResponse()
        if user_agent != payload["agent"]:
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details('user_agent not valid for this token!')
            return UserResponse()
        user = crud.user.get_by(db=db, id=payload['user_id'])
        return UserResponse(id=str(user.id), login=user.login, email=user.email)

    def GetHistory(self, request: UserHistoryRequest, context):
        try:
            db = next(get_db())
            access_token = request.access_token
            user_agent = request.user_agent
            skip = request.skip or 0
            limit = request.limit or 50
            if access_token is None:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details('access_token field required!')
                return UserHistoryResponse()
            if user_agent is None:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details('user_agent field required!')
                return UserHistoryResponse()
            
            payload = decode_token(token=access_token)
            if not check_expire(payload['expire']):
                context.set_code(grpc.StatusCode.UNAUTHENTICATED)
                context.set_details('access_token not valid!')
                return UserHistoryResponse()
            if user_agent != payload["agent"]:
                context.set_code(grpc.StatusCode.UNAUTHENTICATED)
                context.set_details('user_agent not valid for this token!')
                return UserHistoryResponse()

            history = crud.sign_in.get_history(db=db, user_id=payload['user_id'], skip=skip, limit=limit)

            row = [UserHistory(date=str(sign_in.logined_by), user_agent=sign_in.user_agent, device_type=sign_in.user_device_type, active=sign_in.active) for sign_in in history]
            response = UserHistoryResponse(rows=row)
        except Exception as e:
            logger.exception(e)
            context.set_code(grpc.StatusCode.UNKNOWN)
            context.set_details('UNKNOWN error')
            response = UserHistoryResponse()
        finally:
            return response
