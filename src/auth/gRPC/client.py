# import grpc
# from auth_pb2_grpc import UserStub, AuthStub
# from auth_pb2 import UserCreateRequest, LoginRequest
# channel = grpc.insecure_channel("localhost:50051")
# request = UserCreateRequest(login='test', email='test@gmail.com', password='1')
# request = LoginRequest(login='test', password='test@gmail.com', user_agent='text')
# client = AuthStub(channel)
# print(client.Login(request))

#
# import grpc
# from auth_pb2_grpc import UserStub
# from auth_pb2 import UserCreateRequest, UserGetRequest
#
# channel = grpc.insecure_channel("localhost:50051")
#
# request = UserGetRequest(access_token='eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiMTJjNTI5NGEtYzVkNS00NTAyLWIyOTktYjVjZDRiMDJhYzI4IiwiYWdlbnQiOiJTTUFSVCIsIm5vdyI6MTYyMjgxNDgyMC41MTk2MTgsImV4cGlyZSI6MTYyMjgxNTcyMC41MTk2MTh9.PFN3Ez96f0TSbHVHz_z1MPQe5Vuc2ihgRsw-ggpuyXY',
#                          user_agent='SMART')
#
# client = UserStub(channel)
# print(client.Get(request))


# import grpc
# from auth_pb2_grpc import UserStub, AuthStub
# from auth_pb2 import UserCreateRequest, LoginRequest
# channel = grpc.insecure_channel("localhost:50051")
# request = LoginRequest(login='test1', password='1', user_agent='web')
# client = AuthStub(channel)
# print(client.Login(request))


# import grpc
# from auth_pb2_grpc import UserStub, AuthStub
# from auth_pb2 import UserCreateRequest, LoginRequest, RefreshTokenRequest
# channel = grpc.insecure_channel("localhost:50051")
# request = RefreshTokenRequest(refresh_token="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiMTJjNTI5NGEtYzVkNS00NTAyLWIyOTktYjVjZDRiMDJhYzI4IiwiYWdlbnQiOiJTTUFSVCIsIm5vdyI6MTYyMjgxNjc4MS42OTE2MzcsImV4cGlyZSI6MTYyMzQyMTU4MS42OTE2Mzd9.Tz4aS_qcgewYMsdu3Kg0jQJmhht_P4sv6ob1GMjT8cg",
#                               user_agent='SMART')
# client = AuthStub(channel)
# print(client.RefreshToken(request))


# import grpc
# from auth_pb2_grpc import UserStub, AuthStub
# from auth_pb2 import UserCreateRequest, LoginRequest, RefreshTokenRequest, LogoutRequest
# channel = grpc.insecure_channel("localhost:50051")
# request = LogoutRequest(access_token="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiMTJjNTI5NGEtYzVkNS00NTAyLWIyOTktYjVjZDRiMDJhYzI4IiwiYWdlbnQiOiJTTUFSVCIsIm5vdyI6MTYyMjgxNzkwNC44NDkwNjcsImV4cGlyZSI6MTYyMjgxODgwNC44NDkwNjd9.QOTO3OLFx6rgUllgbe7QBsBWlGHhOadT6XTIemHPBS8",
#                         user_agent='SMART')
# client = AuthStub(channel)
# print(client.Logout(request))

import grpc
from auth_pb2_grpc import UserStub, AuthStub
from auth_pb2 import UserHistoryRequest

channel = grpc.insecure_channel("localhost:50051")
request = UserHistoryRequest(
    access_token="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiMTJjNTI5NGEtYzVkNS00NTAyLWIyOTktYjVjZDRiMDJhYzI4IiwiYWdlbnQiOiJTTUFSVCIsIm5vdyI6MTYyMjgxOTM1OC44NzA4OSwiZXhwaXJlIjoxNjIyODIwMjU4Ljg3MDg5fQ.O57oUnOfnIsY6pd982fpM8DKqM0__P0rylQ3RQ0Idtk",
    user_agent="SMART",
)
client = UserStub(channel)
print(client.GetHistory(request))
