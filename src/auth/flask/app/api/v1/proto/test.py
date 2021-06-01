from auth_pb2_grpc import AuthStub
from auth_pb2 import LoginRequest
import grpc
request = LoginRequest(login='sdf', password='asdf')
channel = grpc.insecure_channel("server-auth:50051")
client = AuthStub(channel)
response = client.Login(request)