from app.api.v1.views.auth import auth_ns
from app.api.v1.views.user import user_ns
from flask import Blueprint
from flask_restx import Api

api_bp = Blueprint("api", __name__, url_prefix="/api/v1")
authorizations = {
    "access_token": {"type": "apiKey",
                     "in": "header",
                     "name": "Authorization"},
    "refresh_token": {"type": "apiKey",
                      "in": "header",
                      "name": "Authorization"}
}

api = Api(
    api_bp,
    version="1.0",
    title="API Auth with JWT token",
    description="Welcome to the Swagger UI documentation site!",
    authorizations=authorizations,
)

api.add_namespace(auth_ns, path="/auth")
api.add_namespace(user_ns, path="/user")
