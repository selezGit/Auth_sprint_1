import auth_pb2_grpc
from concurrent import futures
import grpc

import crud
from utils.token import create_access_token, create_refresh_token, check_expire, decode_token
from auth_pb2 import LoginRequest, LoginResponse, RefreshTokenResponse, RefreshTokenRequest, LogoutRequest, \
    LogoutResponse
from db.db import get_db
from loguru import logger
from user_agents import parse


class AuthService(auth_pb2_grpc.AuthServicer):
    def Login(self, request: LoginRequest, context):
        db = next(get_db())
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
        logger.info("validate")
        try:
            if not crud.user.check_password(user=user, password=request.password):
                context.set_code(grpc.StatusCode.UNAUTHENTICATED)
                context.set_details(f"password not valid!")
                return LoginResponse()

            payload = {
                "user_id": str(user.id),
                "agent": request.user_agent
            }

            now, expire_access, access_token = create_access_token(payload=payload)
            now, expire, refresh_token = create_refresh_token(payload=payload)

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

            # TODO add refresh token in white list
        except Exception as e:
            logger.debug(e)
            return LoginResponse()
        logger.info("+")
        try:
            response = LoginResponse(access_token=access_token, refresh_token=refresh_token,
                                     expires_in=str(expire_access),
                                     token_type="Barear")
        except Exception as e:
            logger.info(e)
            return LoginResponse()
        return response

    def RefreshToken(self, request: RefreshTokenRequest, context):
        try:
            user_agent = request.user_agent
            refresh_token = request.refresh_token
            if request.refresh_token is None:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details('refresh_token field required!')
                return LoginResponse()
            if request.user_agent is None:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details('user_agent field required!')
                return LoginResponse()

            payload = decode_token(token=refresh_token)
            if not check_expire(payload['expire']):
                context.set_code(grpc.StatusCode.UNAUTHENTICATED)
                context.set_details('refresh_token not valid!')
                return RefreshTokenResponse()
            if user_agent != payload["agent"]:
                context.set_code(grpc.StatusCode.UNAUTHENTICATED)
                context.set_details('user_agent not valid for this token!')
                return RefreshTokenResponse()

            now, expire_access, access_token = create_access_token(payload=payload)
            now, expire, refresh_token = create_refresh_token(payload=payload)

            response = RefreshTokenResponse(access_token=access_token, refresh_token=refresh_token,
                                            expires_in=str(expire_access),
                                            token_type="Barear")
        except Exception as e:
            logger.exception(e)
            response = RefreshTokenResponse()
        finally:
            return response

    def Logout(self, request: LoginRequest, context):
        try:
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

            payload = decode_token(token=access_token)
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
            # TODO delete refresh_token
            # TODO add access_token to black list
            response = LoginResponse()
        except Exception as e:
            logger.exception(e)
            context.set_code(grpc.StatusCode.UNKNOWN)
            context.set_details('UNKNOWN error')
            response = LoginResponse()
        finally:
            return response
