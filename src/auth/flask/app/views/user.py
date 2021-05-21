from flask import Blueprint, request

bp = Blueprint('user', __name__, url_prefix='/user')


@bp.route('/', methods=('GET', 'POST', 'DELETE'))
async def user():
    if request.method == 'POST':
        pass  # some logics here
    elif request.method == 'DELETE':
        pass  # some logics here
    return 'Hello, World!'


@bp.route('/me', methods=('GET',))
async def user_me():
    if request.method == 'GET':
        pass  # some logics here
    return 'Hello, World!'


@bp.route('/change-password', methods=('GET', 'PATCH'))
async def change_password():
    if request.method == 'PATCH':
        pass  # some logics here
    return 'Hello, World!'


@bp.route('/change-email', methods=('GET', 'PATCH'))
async def change_email():
    if request.method == 'PATCH':
        pass  # some logics here
    return 'Hello, World!'


@bp.route('/history', methods=('GET',))
async def history():
    if request.method == 'GET':
        pass  # some logics here
    return 'Hello, World!'
