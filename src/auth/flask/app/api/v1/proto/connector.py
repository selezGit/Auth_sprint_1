import grpc
from .auth_pb2_grpc import AuthStub


def connect_server_auth():
    channel = grpc.insecure_channel("server-auth:50051")
    client = AuthStub(channel)
    return client