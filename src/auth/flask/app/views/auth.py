from flask import Blueprint, request
from app.proto.auth_pb2 import LoginRequest
from app import client


bp = Blueprint('auth', __name__, url_prefix='/api/v1/auth')




@bp.route('/login', methods=('GET', 'POST'))
async def login():
    # if request.method == 'POST':
    #     pass  # some logics here
    login_data = LoginRequest(login='sdf', password='asdf')
    response = client.Login(login_data)
    print(response)
    return 'Hello, World!'


@bp.route('/refresh', methods=('GET', 'POST'))
async def refresh():
    if request.method == 'POST':
        pass  # some logics here
    return 'Hello, World!'


@bp.route('/logout', methods=('GET', 'POST'))
async def logout():
    if request.method == 'POST':
        pass  # some logics here
    return 'Hello, World!'


@bp.route('/test-token', methods=('GET',))
async def test_token():
    if request.method == 'GET':
        pass  # some logics here
    return 'Hello, World!'
