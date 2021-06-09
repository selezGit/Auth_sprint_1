from functools import wraps
from http import HTTPStatus

import grpc
from flask import jsonify


class LocalException(Exception):
    statuses = {
        grpc.StatusCode.NOT_FOUND: HTTPStatus.NOT_FOUND,
        grpc.StatusCode.INVALID_ARGUMENT: HTTPStatus.BAD_REQUEST,
        grpc.StatusCode.UNAUTHENTICATED: HTTPStatus.UNAUTHORIZED,
        grpc.StatusCode.UNKNOWN: HTTPStatus.SERVICE_UNAVAILABLE,
        grpc.StatusCode.ALREADY_EXISTS: HTTPStatus.CONFLICT
    }

    def get_response(self, status, details):
        response = jsonify(
            status='error',
            details=details
        )
        response.status_code = self.statuses.get(
            status, HTTPStatus.SERVICE_UNAVAILABLE)
        return response


def error_handler(f):
    @wraps(f)
    def inner(*args, **kwargs):
        try:
            return f(*args, **kwargs)

        except grpc.RpcError as rpc_error:
            return LocalException().get_response(status=rpc_error.code(),
                                                 details=rpc_error.details())
    return inner
