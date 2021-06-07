import grpc
from fastapi import Depends, Header
from fastapi.security import HTTPBasicCredentials, HTTPBearer
from proto.auth_pb2 import TestTokenRequest
from proto.connector import ConnectServerGRPC

client = ConnectServerGRPC().conn_auth()
oauth2_scheme = HTTPBearer(scheme_name='access_token')


def check_token(
    access_token: HTTPBasicCredentials = Depends(oauth2_scheme),
    user_agent: str = Header(None)
):
    test_token_data = TestTokenRequest(access_token=access_token.credentials,
                                       user_agent=user_agent)
    try:
        client.TestToken(test_token_data)
        return True
    except grpc.RpcError:
        return False
