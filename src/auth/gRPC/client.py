import grpc
from auth_pb2_grpc import UserStub, AuthStub
from auth_pb2 import UserCreateRequest, LoginRequest
channel = grpc.insecure_channel("localhost:50051")
request = UserCreateRequest(login='test', email='test@gmail.com', password='1')
# request = LoginRequest(login='test', password='test@gmail.com', user_agent='text')
client = UserStub(channel)
# client = AuthStub(channel)
# print(client.Login(request))
