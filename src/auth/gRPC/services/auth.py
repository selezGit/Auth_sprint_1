import auth_pb2_grpc
from concurrent import futures
import grpc

import crud
from utils.token import create_access_token, create_refresh_token, check_expire, decode_token
from auth_pb2 import LoginRequest, LoginResponse, RefreshTokenResponse, RefreshTokenRequest, LogoutRequest, \
    LogoutResponse, TestTokenRequest, TestTokenResponse
from db.db import get_db, db as db_session
from db import no_sql_db as redis_method
from loguru import logger
from user_agents import parse
from datetime import datetime, timedelta, timezone
import jwt
from core.config import settings
from sqlalchemy.exc import IntegrityError
from jwt.exceptions import InvalidTokenError


class AuthService(auth_pb2_grpc.AuthServicer):
    def TestToken(self, request: TestTokenRequest, context):
        db = next(get_db())
        access_token = request.access_token
        user_agent = request.user_agent
        if access_token is None:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('access_token field required!')
            return TestTokenResponse()
        if user_agent is None:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('user_agent field required!')
            return TestTokenResponse()

        try:
            payload = decode_token(token=access_token)

        except InvalidTokenError as e:
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details('access_token not valid!')
            return LoginResponse()
        if not check_expire(payload['expire']):
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details('access_token not valid!')
            return TestTokenResponse()
        if redis_method.check_blacklist(access_token):
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details('access_token not valid!')
            return TestTokenResponse()
        if user_agent != payload["agent"]:
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details('user_agent not valid for this token!')
            return TestTokenResponse()
        return TestTokenResponse()

    def Login(self, request: LoginRequest, context):
        login = request.login
        password = request.password
        user_agent = request.user_agent

        if login is None:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('login field required!')
            return LoginResponse()
        if password is None:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('password field required!')
            return LoginResponse()
        if user_agent is None:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('user_agent field required!')
            return LoginResponse()
        db = next(get_db())

        user = crud.user.get_by(db=db, login=login)
        if user is None:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"user with login: {login} not found!")
            return LoginResponse()

        if not crud.user.check_password(user=user, password=request.password):
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details(f"password not valid!")
            return LoginResponse()

        payload = {
            "user_id": str(user.id),
            "agent": request.user_agent
        }
        refresh_delta = timedelta(days=7)

        now, expire_access, access_token = create_access_token(payload=payload)
        now, expire, refresh_token = create_refresh_token(payload=payload, time=refresh_delta)

        user_agent = parse(request.user_agent)

        if "SMART" in request.user_agent:
            device_type = "smart"
        elif user_agent.is_mobile:
            device_type = "mobile"

        else:
            device_type = "web"

        sign_in = {
            "user_id": user.id,
            "user_device_type": device_type,
            "user_agent": request.user_agent,
        }
        crud.sign_in.create(db=db, obj_in=sign_in)

        redis_method.add_refresh_token(refresh_token=refresh_token, exp=refresh_delta)
        redis_method.add_auth_user(user_id=str(user.id), user_agent=request.user_agent, refresh_token=refresh_token,
                                   exp=refresh_delta)

        response = LoginResponse(access_token=access_token, refresh_token=refresh_token,
                                 expires_in=str(expire_access),
                                 token_type="Barear")

        return response

    def RefreshToken(self, request: RefreshTokenRequest, context):
        user_agent = request.user_agent
        refresh_token = request.refresh_token
        if refresh_token is None:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('refresh_token field required!')
            return LoginResponse()
        if user_agent is None:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('user_agent field required!')
            return LoginResponse()

        try:
            payload = decode_token(token=refresh_token)

        except InvalidTokenError as e:
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details('refresh_token not valid!')
            return LoginResponse()
        if not check_expire(payload['expire']):
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details('refresh_token not valid!')
            return RefreshTokenResponse()
        if user_agent != payload["agent"]:
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details('user_agent not valid for this token!')
            return RefreshTokenResponse()
        if not redis_method.check_whitelist(refresh_token=refresh_token):
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Invalid refresh token!')
            return RefreshTokenResponse()

        check_refresh = redis_method.get_auth_user(payload['user_id'], user_agent=request.user_agent).decode()
        if check_refresh != refresh_token:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Invalid refresh token! -')
            return RefreshTokenResponse()
        redis_method.del_refresh_token(refresh_token=refresh_token)

        # redis_method.del_auth_user(payload['user_id'], refresh_token)

        refresh_delta = timedelta(days=7)
        now, expire_access, access_token = create_access_token(payload=payload)
        payload['access_token'] = access_token
        now, expire, refresh_token = create_refresh_token(payload=payload, time=refresh_delta)

        redis_method.add_refresh_token(refresh_token, exp=refresh_delta)
        redis_method.add_auth_user(payload['user_id'], request.user_agent, refresh_token, exp=refresh_delta)

        response = RefreshTokenResponse(access_token=access_token, refresh_token=refresh_token,
                                        expires_in=str(expire_access),
                                        token_type="Barear")
        return response

    def Logout(self, request: LoginRequest, context):
        db = next(get_db())
        access_token = request.access_token
        user_agent = request.user_agent

        if access_token is None:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('access_token field required!')
            return LogoutResponse()
        if user_agent is None:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('user_agent field required!')
            return LogoutResponse()
        if redis_method.check_blacklist(access_token):
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('access_token not valid!')
            return LogoutResponse()
        try:
            payload = decode_token(token=access_token)

        except InvalidTokenError as e:
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details('access_token not valid!')
            return LoginResponse()
        if not check_expire(payload['expire']):
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details('access_token not valid!')
            return LogoutResponse()
        if user_agent != payload["agent"]:
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details('user_agent not valid for this token!')
            return LogoutResponse()

        sign_in = crud.sign_in.get_by(db=db, user_id=payload['user_id'], user_agent=user_agent)
        crud.sign_in.update(db=db, db_obj=sign_in, obj_in={"active": False})
        refresh_token = redis_method.get_auth_user(payload['user_id'], request.user_agent)
        redis_method.del_refresh_token(refresh_token)
        redis_method.del_auth_user(payload['user_id'], request.user_agent)
        exp_for_black_list = datetime.fromtimestamp(payload['expire'], timezone.utc) - datetime.now(timezone.utc)
        redis_method.add_to_blacklist(access_token, exp=exp_for_black_list)
        response = LoginResponse()
        return response
