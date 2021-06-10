import auth_pb2_grpc
from concurrent import futures
import grpc

from db.db import init_db

from services.user import UserService
from services.auth import AuthService

from loguru import logger


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=6))
    auth_pb2_grpc.add_AuthServicer_to_server(AuthService(), server)
    auth_pb2_grpc.add_UserServicer_to_server(UserService(), server)
    server.add_insecure_port('[::]:50051')

    server.start()
    logger.info('Server startup.')
    server.wait_for_termination()

if __name__ == '__main__':
    init_db()
    serve()
