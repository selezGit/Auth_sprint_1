from http import HTTPStatus

from flask import current_app, jsonify
from flask_restx import abort

from flask_api_tutorial import db
from flask_api_tutorial.api.auth.decorators import token_required
from db.db_models import User








def process_registration_request(email, password):
    if User.find_by_email(email):
        abort(HTTPStatus.CONFLICT, f"{email} is already registered", status="fail")
    new_user = User(email=email, password=password)
    db.session.add(new_user)
    db.session.commit()
    access_token = new_user.encode_access_token()
    return _create_auth_successful_response(
        token=access_token.decode(),
        status_code=HTTPStatus.CREATED,
        message="successfully registered",
    )