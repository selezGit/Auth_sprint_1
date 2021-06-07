from http import HTTPStatus

from app.api.v1.exceptions import error_handler
from app.api.v1.proto.auth_pb2 import (UserCreateRequest, UserDeleteMe,
                                       UserGetRequest, UserHistoryRequest,
                                       UserUpdateEmailRequest,
                                       UserUpdatePasswordRequest)
from app.api.v1.proto.connector import ConnectServerGRPC
from flask import jsonify
from google.protobuf.json_format import MessageToDict

client = ConnectServerGRPC().conn_user()


@error_handler
def create_user_logic(login: str, email: str, password: str):
    create_user_data = UserCreateRequest(
        login=login, email=email, password=password)
    request = MessageToDict(client.Create(create_user_data))
    response = jsonify(request)
    response.status_code = HTTPStatus.CREATED
    return response


@error_handler
def delete_user_logic(access_token: str, user_agent: str):
    delete_user_data = UserDeleteMe(access_token, user_agent)
    request = client.DeleteMe(delete_user_data)
    print(request)
    # TODO логика удаления не работает, выкидывает ошибку
    return jsonify(message='user successfully deleted')


@error_handler
def get_user_logic(access_token: str, user_agent: str):
    get_user_data = UserGetRequest(
        access_token=access_token, user_agent=user_agent)
    request = MessageToDict(client.Get(get_user_data))
    return jsonify(request)


@error_handler
def history_logic(access_token: str, user_agent: str):
    history_data = UserHistoryRequest(
        access_token=access_token, user_agent=user_agent)
    request = MessageToDict(client.GetHistory(history_data))
    return jsonify(request)


@error_handler
def change_password_logic(old_password: str, new_password: str,
                          access_token: str, user_agent: str):
    change_password_data = UserUpdatePasswordRequest(old_password=old_password,
                                                     new_password=new_password,
                                                     access_token=access_token,
                                                     user_agent=user_agent)
    request = client.UpdatePassword(change_password_data)
    print(request)
    # TODO не работает
    return jsonify(status='Success')


@error_handler
def change_email_logic(password: str, email: str,
                       access_token: str, user_agent: str):
    upate_email_data = UserUpdateEmailRequest(password=password,
                                              email=email,
                                              access_token=access_token,
                                              user_agent=user_agent)
    request = client.UpdateEmail(upate_email_data)
    print(request)
    # TODO не работает

    return jsonify(status='Success')
