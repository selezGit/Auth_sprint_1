from http import HTTPStatus

import grpc
from flask import jsonify


class LocalException(Exception):
    statuses = {
        grpc.StatusCode.NOT_FOUND: HTTPStatus.NOT_FOUND,
        grpc.StatusCode.INVALID_ARGUMENT: HTTPStatus.BAD_REQUEST,
        grpc.StatusCode.UNAUTHENTICATED: HTTPStatus.UNAUTHORIZED,
        grpc.StatusCode.UNKNOWN: HTTPStatus.SERVICE_UNAVAILABLE
    }

    def get_response(self, status, details):
        response = jsonify(
            status='error',
            details=details
        )
        response.status_code = self.statuses.get(
            status, HTTPStatus.SERVICE_UNAVAILABLE)
        return response


error_handler = LocalException()
