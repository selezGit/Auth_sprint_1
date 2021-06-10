from datetime import datetime, timezone

import auth_pb2_grpc
import crud
import grpc
from auth_pb2 import (UserCreateRequest, UserDeleteMe, UserGetRequest,
                      UserHistory, UserHistoryRequest, UserHistoryResponse,
                      UserResponse, UserUpdateEmailRequest,
                      UserUpdatePasswordRequest)
from db import no_sql_db as redis_method
from db.db import get_db
from jwt.exceptions import InvalidTokenError
from loguru import logger
from sqlalchemy.exc import IntegrityError
from utils.token import check_expire, decode_token


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
                'login': request.login,
                'email': request.email,
                'password': request.password
            })
        except IntegrityError as e:
            logger.exception(e.orig.diag.message_detail)
            context.set_code(grpc.StatusCode.ALREADY_EXISTS)
            context.set_details(e.orig.diag.message_detail)
            return UserResponse()
        except Exception as e:
            logger.exception(e)
            context.set_code(grpc.StatusCode.WARNING)
            context.set_details()
            return UserResponse()
        user_response = UserResponse(
            id=str(user.id), login=user.login, email=user.email)
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
        if redis_method.check_blacklist(access_token):
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details('access_token not valid!')
            return UserResponse()
        if not check_expire(payload['expire']):
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details('access_token not valid!')
            return UserResponse()

        if user_agent != payload['agent']:
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
        if redis_method.check_blacklist(access_token):
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details('access_token not valid!')
            return UserHistoryResponse()
        if user_agent != payload['agent']:
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details('user_agent not valid for this token!')
            return UserHistoryResponse()

        history = crud.sign_in.get_history(
            db=db, user_id=payload['user_id'], skip=skip, limit=limit)

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
            payload = decode_token(token=access_token)

        except InvalidTokenError as e:
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details('access_token not valid!')
            return UserResponse()

        if redis_method.check_blacklist(access_token):
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details('access_token not valid!')
            return UserResponse()

        if not check_expire(payload['expire']):
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details('access_token not valid!')
            return UserResponse()
        if user_agent != payload['agent']:
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details('user_agent not valid for this token!')
            return UserResponse()

        user = crud.user.get_by(db=db, id=payload['user_id'])
        if not crud.user.check_password(user=user, password=password):
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(f'password not valid!')
            return UserResponse()

        try:
            user = crud.user.update(
                db=db, db_obj=user, obj_in={'email': email})
        except IntegrityError as e:
            logger.exception(e.orig.diag.message_detail)
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(e.orig.diag.message_detail)
            return UserResponse()
        response = UserResponse(
            id=str(user.id), email=user.email, login=user.login)
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
            payload = decode_token(token=access_token)

        except InvalidTokenError as e:
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details('access_token not valid!')
            return UserResponse()

        if not check_expire(payload['expire']):
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details('access_token not valid!')
            return UserResponse()
        if redis_method.check_blacklist(access_token):
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details('access_token not valid!')
            return UserResponse()
        if user_agent != payload['agent']:
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details('user_agent not valid for this token!')
            return UserResponse()
        user = crud.user.get_by(db=db, id=payload['user_id'])
        if not crud.user.check_password(user=user, password=old_password):
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details(f'password not valid!')
            return UserResponse()
        user = crud.user.update(db=db, db_obj=user, obj_in={
                                'password': new_password})

        all_auth = redis_method.get_all_auth_user(payload['user_id'])

        for _, ref in all_auth.items():
            try:
                payload = decode_token(token=access_token)
            except InvalidTokenError as e:
                pass
            exp_for_black_list = datetime.fromtimestamp(
                payload['expire'], timezone.utc) - datetime.now(timezone.utc)
            redis_method.add_to_blacklist(
                access_token, exp=exp_for_black_list)
            
            redis_method.del_refresh_token(ref.decode())
        redis_method.del_all_auth_user(payload['user_id'])
        response = UserResponse(
            id=str(user.id), email=user.email, login=user.login)
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
            payload = decode_token(token=access_token)

        except InvalidTokenError as e:
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details('access_token not valid!')
            return UserResponse()
        if redis_method.check_blacklist(access_token):
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details('access_token not valid!')
            return UserResponse()
        if not check_expire(payload['expire']):
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details('access_token not valid!')
            return UserResponse()
        if user_agent != payload['agent']:
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details('user_agent not valid for this token!')
            return UserResponse()
        user = crud.user.get_by(db=db, id=payload['user_id'])
        if not crud.user.check_password(user=user, password=password):
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(f'password not valid!')
            return UserResponse()

        all_auth = redis_method.get_all_auth_user(payload['user_id'])

        for _, ref in all_auth.items():
            try:
                payload = decode_token(token=access_token)
            except InvalidTokenError as e:
                pass
            exp_for_black_list = datetime.fromtimestamp(
                payload['expire'], timezone.utc) - datetime.now(timezone.utc)
            redis_method.add_to_blacklist(
                access_token, exp=exp_for_black_list)
            
            redis_method.del_refresh_token(ref.decode())
        redis_method.del_all_auth_user(payload['user_id'])
        crud.user.remove(db=db, db_obj=user)
        return UserResponse()
