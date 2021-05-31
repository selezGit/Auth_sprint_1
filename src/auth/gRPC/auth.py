import auth_pb2_grpc
from concurrent import futures
from db.db import init_db

import grpc

from auth_pb2 import LoginRequest, LoginResponse


class AuthService(auth_pb2_grpc.AuthServicer):
    def Login(self, request, context):
        return LoginResponse(access_token="Hello", refresh_token="Token", expires_in="3000", token_type="Barear")

def serve():
    init_db()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=6))
    auth_pb2_grpc.add_AuthServicer_to_server(
        AuthService(), server
    )
    server.add_insecure_port("[::]:50051")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()