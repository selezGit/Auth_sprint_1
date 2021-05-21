from flask import Blueprint, request

bp = Blueprint('auth', __name__)


@bp.route('/login', methods=('GET', 'POST'))
async def login():
    if request.method == 'POST':
        pass  # some logics here
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
