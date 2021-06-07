import auth_pb2_grpc
from auth_pb2 import UserResponse, UserCreateRequest, UserGetRequest, UserHistoryResponse, UserHistory, \
    UserHistoryRequest, \
    UserUpdateEmailRequest, UserUpdatePasswordRequest, UserDeleteMe
import grpc
from db.db import get_db, db as db_session
import crud
from pathlib import Path
from loguru import logger
from utils.token import decode_token, check_expire
from sqlalchemy.exc import IntegrityError

from jwt.exceptions import InvalidKeyError, InvalidSignatureError, InvalidTokenError, DecodeError

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
        try:
            user = crud.user.create(db=db, obj_in={
                "login": request.login,
                "email": request.email,
                "password": request.password
            })
        except IntegrityError as e:
            logger.exception(e.orig.diag.message_detail)
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(e.orig.diag.message_detail)
            return UserResponse()
        except Exception as e:
            logger.exception(e)
            context.set_code(grpc.StatusCode.WARNING)
            context.set_details()
            return UserResponse()
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
        try:
            payload = decode_token(token=access_token)

        except InvalidTokenError as e:
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details('access_token not valid!')
            return UserResponse()

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
        try:
            payload = decode_token(token=access_token)

        except InvalidTokenError as e:
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details('access_token not valid!')
            return UserResponse()
        if not check_expire(payload['expire']):
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details('access_token not valid!')
            return UserHistoryResponse()
        if user_agent != payload["agent"]:
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details('user_agent not valid for this token!')
            return UserHistoryResponse()

        history = crud.sign_in.get_history(db=db, user_id=payload['user_id'], skip=skip, limit=limit)

        row = [UserHistory(date=str(sign_in.logined_by), user_agent=sign_in.user_agent,
                           device_type=sign_in.user_device_type, active=sign_in.active) for sign_in in history]
        response = UserHistoryResponse(rows=row)
        return response

    def UpdateEmail(self, request: UserUpdateEmailRequest, context):
        db = next(get_db())
        if request.access_token is None:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('access_token field required!')
            return UserResponse()
        if request.user_agent is None:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('user_agent field required!')
            return UserResponse()
        if request.email is None:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('email field required!')
            return UserResponse()
        if request.password is None:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('password field required!')
            return UserResponse()
        access_token = request.access_token
        user_agent = request.user_agent
        email = request.email
        password = request.password
        try:
            # TODO проверка access_token на наличие в black list
            payload = decode_token(token=access_token)

        except InvalidTokenError as e:
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details('access_token not valid!')
            return UserResponse()

        if not check_expire(payload['expire']):
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details('access_token not valid!')
            return UserResponse()
        if user_agent != payload["agent"]:
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details('user_agent not valid for this token!')
            return UserResponse()

        user = crud.user.get_by(db=db, id=payload['user_id'])
        if not crud.user.check_password(user=user, password=password):
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details(f"password not valid!")
            return UserResponse()

        try:
            user = crud.user.update(db=db, db_obj=user, obj_in={'email': email})
        except IntegrityError as e:
            logger.exception(e.orig.diag.message_detail)
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(e.orig.diag.message_detail)
            return UserResponse()
        response = UserResponse(id=str(user.id), email=user.email, login=user.login)
        return response

    def UpdatePassword(self, request: UserUpdatePasswordRequest, context):

        db = next(get_db())
        access_token = request.access_token
        user_agent = request.user_agent
        new_password = request.new_password
        old_password = request.old_password
        if access_token is None:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('access_token field required!')
            return UserResponse()
        if user_agent is None:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('user_agent field required!')
            return UserResponse()
        if new_password is None:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('new_password field required!')
            return UserResponse()
        if old_password is None:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('password field required!')
            return UserResponse()
        try:
            # TODO проверка access_token на наличие в black list
            payload = decode_token(token=access_token)

        except InvalidTokenError as e:
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details('access_token not valid!')
            return UserResponse()
        if not check_expire(payload['expire']):
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details('access_token not valid!')
            return UserResponse()
        if user_agent != payload["agent"]:
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details('user_agent not valid for this token!')
            return UserResponse()
        user = crud.user.get_by(db=db, id=payload['user_id'])
        if not crud.user.check_password(user=user, password=old_password):
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details(f"password not valid!")
            return UserResponse()
        user = crud.user.update(db=db, db_obj=user, obj_in={'password': new_password})

        # TODO мб стоит сбрасывать все access_code и refresh_code
        response = UserResponse(id=str(user.id), email=user.email, login=user.login)
        return response

    def DeleteMe(self, request: UserDeleteMe, context):
        db = next(get_db())
        access_token = request.access_token
        user_agent = request.user_agent
        password = request.password
        if access_token is None:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('access_token field required!')
            return UserResponse()
        if user_agent is None:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('user_agent field required!')
            return UserResponse()
        if password is None:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('password field required!')
            return UserResponse()
        try:
            # TODO проверка access_token на наличие в black list
            payload = decode_token(token=access_token)

        except InvalidTokenError as e:
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details('access_token not valid!')
            return UserResponse()
        if not check_expire(payload['expire']):
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details('access_token not valid!')
            return UserResponse()
        if user_agent != payload["agent"]:
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details('user_agent not valid for this token!')
            return UserResponse()
        user = crud.user.get_by(db=db, id=payload['user_id'])
        if not crud.user.check_password(user=user, password=password):
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details(f"password not valid!")
            return UserResponse()
        # TODO delete all key in redis this user
        crud.user.remove(db=db, db_obj=user)
        return UserResponse()