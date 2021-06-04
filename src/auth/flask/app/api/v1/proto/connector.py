import grpc
from app.api.v1.proto.auth_pb2_grpc import AuthStub, UserStub



class ConnectServerGRPC:
    channel = grpc.insecure_channel("server-auth:50051")

    def conn_auth(self):
        return AuthStub(self.channel)

    def conn_user(self):
        return UserStub(self.channel)